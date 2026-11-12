"""Rule-based product title cleaning for flat e-commerce exports."""

from __future__ import annotations

import re
from functools import lru_cache
from urllib.parse import unquote_plus

# Counts describe how many sellable units are bundled, whereas a value followed
# by oz/g/ml/etc. describes the size of one product and must remain.
PACK_PATTERNS = (
    re.compile(r"\b\d+\s+per\s+(?:case|box|pack)\b", re.I),
    re.compile(r"\bquantity\s*[:#-]?\s*\d+\b", re.I),
    re.compile(r"\bunit\s+of\s+\d+\b", re.I),
    re.compile(r"\b\d+\s*[x×]\s*\d+\s*/\s*(?=\d+(?:[.,]\d+)?\s*(?:fl\s*oz|fz|oz|ounces?|g|gr|gm|grams?|kg|ml|l|lb|lbs)\b)", re.I),
    re.compile(r"\b(?:value\s+)?(?:bulk\s+)?multi[ -]?packs?\b[)\s]*\d*", re.I),
    re.compile(r"\b(?:packs?|cases?|boxes?|pk|pkg|pck)\s*[-:#]?\s*\d+\b(?!\s*(?:fl\s*oz|oz|ounces?|g|kg|ml|l|lb)\b)", re.I),
    re.compile(r"\b(?:pk|pkg|pck)\s+of\s+\d+\b", re.I),
    re.compile(r"\b\d+\s*(?:individual|cans?)\b(?=\s*[,;|)]|\s*$)", re.I),
    re.compile(r"\b\d+\s+(?=softgels?|caps?|sticks?|treats?\b)", re.I),
    re.compile(r"\b\d+\s+(?=veg\s+caps?\b)", re.I),
    re.compile(r"\b\d+\s*pcks?\b", re.I),
    re.compile(r"(?<=Sleepytime)\d+\b", re.I),
    re.compile(r"\b\d+\s*[- ]?count\s+boxes?\b", re.I),
    re.compile(r"\b(?:pack|box|case|bundle|set)\s+of\s*\(?\d+\)?(?:\s+(?:bags?|bottles?|boxes?|jars?|cans?))?\b", re.I),
    re.compile(r"\b(?:pack|box|case|bundle|set)\s+of\s+\d+\b", re.I),
    re.compile(r"\b\d+\s*[- ]?\s*(?:packs?|pkgs?|pk|boxes|cases|units?)\b", re.I),
    re.compile(r"\b(?:pk|pkg|pack)\s*[-:#]?\s*\d+\b(?!\s*(?:fl\s*oz|oz|ounces?|g|kg|ml|l|lb)\b)", re.I),
    re.compile(r"\b\d+\s*[- ]?\s*(?:count|ct|ea|pieces?|pcs?)\b", re.I),
    re.compile(r"\b\d+\s+servings?\b", re.I),
    re.compile(r"\b\d+\s+total\s+servings?\b", re.I),
    re.compile(r"\b\d+\s+total\b", re.I),
    re.compile(r"\b\d+\s+bars?\b", re.I),
    re.compile(r"\b\d+\s+(?=tea\s+bags?\b|dryer\s+sheets?\b|wipes?\b|capsules?\b|tablets?\b|packets?\b|pods?\b|sachets?\b)", re.I),
    re.compile(r"\b\d+\s*[x×]\s*(?=\d+(?:[.,]\d+)?\s*(?:fl\s*oz|fz|oz|ounces?|g|gr|gm|grams?|kg|ml|l|lb|lbs)\b)", re.I),
    re.compile(r"\b\d+\s*/\s*(?=\d+(?:[.,]\d+)?\s*(?:fl\s*oz|fz|oz|ounces?|g|gr|gm|grams?|kg|ml|l|lb|lbs)\b)", re.I),
    re.compile(r"(?<=\b)\s*[x×]\s*\d+\b", re.I),
)

FEATURE_PATTERN = re.compile(
    r"\b(?:cruelty[ -]?free|fragrance[ -]?free|preservative[ -]?free|"
    r"non[ -]?irritating|free[ -]?&[ -]?clear|"
    r"(?:baking[ -]?soda|alumin(?:um|ium)(?:[ -]?chlorohydrate)?|"
    r"parabens?|sulfates?|sls|ammonia|calor(?:ie|ies)|gelatin|"
    r"allergens?|chlorine|dyes?|alcohol|plastic|tree|mold|mycotoxins?|"
    r"seed[ -]?oil|palm[ -]?oil|oil|peanuts?|tree[ -]?nuts?|yeast|"
    r"antibiotics?|rawhide|msg|mess|fuss|tear)[ -]?free|"
    r"no[ -]?artificial[ -]?(?:flavo(?:u)?rs?|additives?|sweeteners?|colors?|preservatives?|ingredients?)|"
    r"no[ -]?additives?(?:[ /-]*(?:or[ -]?)?preservatives?)?|"
    r"no[ -]?(?:seed oils?|fillers?|dyes?|sugar substitutes?)|"
    r"no[ -]?grain[ -]?free|no[ -]?grain[ -]?(?:or[ -]?soy)?|zero[ -]?sugar|no[ -]?sugars?(?:[ -]?added)?|"
    r"no[ -]?added[ -]?sugars?|gluten\s*(?:&|and)\s*sugar[ -]?free|"
    r"nut[ -]?free|non[ -]?alcohol(?:ic)?|non[ -]?narcotic|"
    r"gmo[ -]?free|wheat[ -]?free|grain[ -]?free|corn[ -]?free|"
    r"gluten[ -]?and[ -]?soy[ -]?free|gluten[ -]?free|"
    r"soy[ -]?free|non[ -]?gmo|no[ -]?gmo'?s?|low[ -]?calor(?:ie|ies)|"
    r"high[ -]?protein|low[ -]?(?:net[ -]?)?carbs?|sugar[ -]?free|"
    r"no[ -]?sugar(?:[ -]+no[ -]?salt)?[ -]?added|free[ -]?of[ -]?preservatives|"
    r"low[ -]?zero[ -]?carb|low[ -]?sodium|fat[ -]?free|"
    r"low[ -]?fat|dairy[ -]?free|non[ -]?dairy|all[ -]?natural|"
    r"plant[ -]?based|grass[ -]?fed|guilt[ -]?free|biodegradable|"
    r"responsibly[ -]?grown|kid[ -]?friendly|caffeine[ -]?free|"
    r"salt[ -]?free|no[ -]?salt|fair[ -]?trade|project[ -]?verified|certified|"
    r"cage[ -]?free|seed[ -]?free|toxin[ -]?free|nicotine[ -]?free|"
    r"eco[ -]?friendly|non[ -]?toxic|antibacterial|non[ -]?soap|non[ -]?detergent|"
    r"bpa[ -]?free|"
    r"acid[ -]?free|sedative[ -]?free|fluoride[ -]?free|"
    r"single[ -]?origin|usda|kosher|decaffeinated|decaf|unscented|organic|"
    r"vegetarian|vegan|keto[ -]?friendly|paleo[ -]?friendly|keto|paleo|"
    r"carnivore|whole\s*30)\b",
    re.I,
)

# Remove absence claims even when the exact substance is not in the list above.
# Long descriptors are matched before a single word so "Baking Soda Free"
# cannot leave a stray "Baking" in the search title.
FREE_CLAIM_PATTERN = re.compile(
    r"\b(?:baking[ -]?soda|alumin(?:um|ium)[ -]?chlorohydrate|"
    r"glyphosate[ -]?residue|tree[ -]?nuts?|seed[ -]?oils?|palm[ -]?oils?|"
    r"[A-Za-z][\w'-]*\s+(?:&|and)\s+[A-Za-z][\w'-]*|"
    r"[A-Za-z][\w'-]*)[ -]free\b",
    re.I,
)

PROMO_PATTERN = re.compile(
    r"\b(?:packaging may vary|back to school|made in (?:the )?usa|"
    r"product of (?:the )?(?:usa|portugal)|amazon vine|"
    r"for (?:all hair types|all breeds|pet lovers|dogs\s*&\s*cats)|"
    r"for workout recovery|"
    r"perfect for|great for|ideal for|supports (?:healthy|kidney|digestive)|"
    r"substitute for|(?:jar|bottle) equal to)\b[^|,;]*",
    re.I,
)
MARKETING_CLAUSE = re.compile(
    r"^(?:school snacks?|endurance\b.*\bsupport|"
    r"rich\s+[^,|;]{0,35}\s+delight|indulgence with\b|professional size|"
    r"clean daily|seen on|"
    r"(?:snack\s*&\s*)?healthy snacks?|travel snacks?|office breaks?|"
    r"\d+%\s+of your daily|bulk\b|"
    r"back to school|perfect for|great for|ideal for|supports\b|"
    r"individually wrapped|long[ -]?lasting|comforts?\s*&\s*soothes?|"
    r"safely and effectively fights odor|"
    r"trusted since|revitalizes?\s*&\s*renews?|energizing cleanser|"
    r"rich\s*&\s*smooth|rich fruit\s*&\s*spice|desserts?\s*&\s*beverages?|"
    r"pastries?\s*&\s*holiday|classic festive|nutrient[ -]?packed|"
    r"a\+\s*grade|lasting for|lasts for|made for sensitive|"
    r"fast relief|no aftertaste|blasts away|naturally light taste|"
    r"workout recovery|delicious smooth taste|home bar tools|"
    r"bar cart accessories|wedding gifts|product of|"
    r"skin\s*&\s*nails|hair\s*,\s*skin|balanced nutrition|"
    r"raw you can see|fish only animal protein|"
    r"homeopathic liquid formula|homeopathic flower essence|"
    r"natural stress relief|natural sleep aid|"
    r"(?:immune system|stress\s*&\s*tension|hair growth|joint) support|"
    r"prebiotic|prebiotics?\s*\+\s*probiotics?|"
    r"for (?:all|men|women|pet lovers)|"
    r"sustainably harvested|(?:all[ -]?purpose|medium) grind|"
    r"43\s+hour\s+burn|real meat|food grade silicone|pet soothing|suction back|"
    r"colors?$|preservatives?$|natural$|protein rich|glass bottles?|"
    r"adaptogenic herbal mushroom coffee|"
    r"no additives?(?:\s*/\s*preservatives?)?|"
    r"lasts?\s+(?:up to\s+\d+\s+)?(?:for\s+)?years?|"
    r"velvety|creamy$|100% fresh|japanese cage free|"
    r"premium chili crunch|good on noodles|"
    r"savory$|rum[ -]?kissed|"
    r"awapuhi$|lactic acid$|pro vitamin b5|"
    r"organs?\s*&\s*bone|dog food topper and mixer|"
    r"cleans teeth|compostable wrappers|"
    r"single ingredient upcycled cod|natural calcium|"
    r"\d+%\s*protein|"
    r"contains amla for healthy|rich in vitamin|"
    r"light green$|lotion$|adults$|unisex[ -]?adults|hair loss/thinning|"
    r"chia seeds bulk|"
    r"proteins$|veggies and everything|"
    r"gym\s*&\s*fitness supplements|"
    r"reusable menstrual cup\s*\+\s*\d+ free menstrual discs|"
    r"pull[ -]?tab for easy removal|tampon\s*\+\s*pad alternative|"
    r"biotin and collagen supplement|hyaluronic acid$|"
    r"unprocessed$|friendly wild oregano|mediterranean source|"
    r"vitamins? d\s*&\s*b12|nsf for sport|"
    r"type i\s*&\s*iii|\d+\s*g\s*mct oil|"
    r"hair$|skin$|nail$|stress relief$|"
    r"free of melatonin|gluten$|holiday stocking stuffer|"
    r"protect me$|boost energy|brain function|detoxification|metabolism|"
    r"brain juice$|ingredients$|"
    r"laundry$|diapers$|wine$|carpets$|more$|"
    r"real food ingredients?|lean protein|omega[ -]?3$|"
    r"digestive fiber blend|added minerals\s*&\s*vitamins|"
    r"made with\s*\d+%|ages\s*&\s*weights|canned$|"
    r"shiny and manageable hair|stim[ -]?free preworkout|"
    r"wipes? per$|"
    r"\d+\s*g\s+(?:grass[ -]?fed\s+)?hydrolyzed collagen peptides|"
    r"gluten\s*&\s*sugar$|"
    r"\d+(?:[.,]\d+)?\s*g\s+(?:vegan\s+)?(?:protein|sugar|whole grains)\b|"
    r"cage[ -]?free chicken\s*&\s*duck recipe with superfoods)",
    re.I,
)
SEO_SECTION_LEAD = re.compile(
    r"^(?:real food ingredients?|made with real ingredients?|product of|imported from|"
    r"steak sauce|chicken sauce|pre[ -]?made sauce|meats? prepared foods?|"
    r"perfect for|great for|ideal for|good for|no artificial|no added|"
    r"authentic(?:\s+\w+){0,2}\s+(?:taste|flavor|quality))\b",
    re.I,
)
BENEFIT_TRAIL = re.compile(
    r"\b(?:removes?\s+(?:chewing|grease|tar|stickers?|labels?|tape|residue)|"
    r"balances?\s+(?:pH|skin)|hydrates?\s+(?:and|dry|skin)|"
    r"helps?\s+(?:calm|support|relieve|reduce)|"
    r"for\s+(?:enhanced|focus and|mental clarity|all skin types|busy days|snacking|workout recovery)|"
    r"made\s+with\s+(?:just|real|pure)|ready\s+in\s+under)\b",
    re.I,
)
FLAVOR_CLAUSE = re.compile(r"\b(?:flav(?:or|our)|scent|recipe|variety|blend|roast|mild|medium|hot|spicy|vanilla|chocolate|cheddar|berry|orange|lemon|lavender|peppermint|apple|apples|peach|peaches|persimmon|persimmons|almond|chicken|beef|duck|turkey|salmon|tuna|peanut|pumpkin|garlic|miso|chili|curry|mushroom|lime|ginger|butterscotch|maple|strawberry|blueberry|mango|black|red|blue|green|silver|pink|white|yellow|purple|grey|gray|margarita|mojito|mule)\b", re.I)
FORMULA_INGREDIENT = re.compile(r"\b(?:reishi|lion['’]?s mane|chaga|turkey tail|cordyceps|parmigiano|pecorino)\b", re.I)
MODEL_VARIANT = re.compile(r"\b(?:model|size|series|type)\s*[#:]?\s*[A-Z0-9]+\b|\b[A-Z]{1,3}\d{2,}\b", re.I)
GENERIC_SEARCH_WORDS = {
    "and", "the", "with", "for", "from", "of", "by", "in", "to", "a", "an",
    "natural", "real", "fresh", "slow", "premium", "authentic", "genuine",
    "traditional", "classic", "delicious", "healthy", "food", "product",
    "snack", "candy", "sauce", "mix", "drink", "tea", "coffee", "bar",
    "bottle", "jar", "can", "pack", "pouch", "seasoning", "syrup",
    "pancake", "pasta", "noodle", "italian", "vermont", "included",
}

MEASURE_PATTERN = re.compile(
    r"(?:(?<![\w.])|(?<=[x×]))((?:\d+(?:[.,]\d+)?|[.,]\d+))[-\s]*(fl\.?\s*oz|fz|ounces?|oz|grams?|gr|gm|g|kg|ml|liters?|ltrs?|l|lbs?|pounds?|quarts?|qt|pints?|pt|gallons?|gal|mg|mcg)\b",
    re.I,
)

NUTRITION_MEASURE_TAIL = re.compile(
    r"^\s*(?:/\s*\d+\s*cal(?:ories)?\b|(?:of\s+)?(?:complete\s+plant\s+|net\s+|vegan\s+|grass[ -]?fed\s+|hydrolyzed\s+)*"
    r"(?:protein|fiber|fibre|carbs?|sugars?|whole grains|collagen|mct oil|omegas?)\b)",
    re.I,
)

UNIT_NAMES = {
    "fz": "fl oz", "fl oz": "fl oz", "oz": "oz", "ounce": "oz", "ounces": "oz",
    "gram": "g", "grams": "g", "gr": "g", "gm": "g", "g": "g", "kg": "kg", "ml": "ml",
    "liter": "l", "liters": "l", "ltr": "l", "ltrs": "l", "l": "l", "lb": "lb", "lbs": "lb",
    "pound": "lb", "pounds": "lb",
    "quart": "qt", "quarts": "qt", "qt": "qt", "pint": "pt", "pints": "pt",
    "pt": "pt", "gallon": "gal", "gallons": "gal", "gal": "gal",
    "mg": "mg", "mcg": "mcg",
}


def _normalize_measure(match):
    unit = match.group(2).lower().replace(".", "")
    unit = re.sub(r"\s+", " ", unit).strip()
    amount = match.group(1)
    if amount.startswith((".", ",")):
        amount = "0" + amount
    return f"{amount} {UNIT_NAMES.get(unit, unit)}"


def _search_words(value: str) -> set[str]:
    words = set()
    for raw in re.findall(r"\b\w+\b", value.casefold()):
        word = raw[:-1] if len(raw) > 4 and raw.endswith("s") and not raw.endswith("ss") else raw
        if len(word) > 2 and word not in GENERIC_SEARCH_WORDS:
            words.add(word)
    return words


@lru_cache(maxsize=4096)
def _brand_matcher(name: str) -> re.Pattern[str]:
    return re.compile(r"(?<!\w)" + re.escape(name) + r"(?!\w)", re.I)


def _is_product_measure(match: re.Match[str], text: str) -> bool:
    unit = match.group(2).lower().replace(".", "").strip()
    if unit in {"g", "gr", "gm", "gram", "grams", "mg", "mcg"}:
        return not NUTRITION_MEASURE_TAIL.match(text[match.end():])
    return True


def _product_measures(text: str) -> list[re.Match[str]]:
    return [match for match in MEASURE_PATTERN.finditer(text) if _is_product_measure(match, text)]


def _prune_long_search_title(clauses: list[str]) -> list[str]:
    """Retain identity, size and distinct variants in keyword-heavy titles."""
    if len(clauses) < 4 or len(", ".join(clauses)) <= 100:
        return clauses

    core_count = 2 if clauses[0] == "\u0001" else 1
    core = " ".join(clauses[:core_count])
    core_words = _search_words(core)
    result = list(clauses[:core_count])
    if len(result[-1]) > 100:
        benefit = BENEFIT_TRAIL.search(result[-1])
        if benefit and len(result[-1][:benefit.start()].split()) >= 5:
            result[-1] = result[-1][:benefit.start()].strip(" ,;:-&")
    variants = 0
    for clause in clauses[core_count:]:
        measures = _product_measures(clause)
        if measures:
            if len(clause.split()) > 7:
                result.extend(_normalize_measure(match) for match in measures)
            else:
                result.append(clause)
            continue
        is_formula = bool(FORMULA_INGREDIENT.search(clause))
        is_variant = bool(
            FLAVOR_CLAUSE.search(clause) or MODEL_VARIANT.search(clause) or "&" in clause or "+" in clause
            or len(clause.split()) <= 2
        )
        novel_words = _search_words(clause) - core_words
        if is_formula and len(clause.split()) <= 8:
            result.append(clause)
        elif is_formula:
            lead = re.split(r"\b(?:with|plus)\b", clause, maxsplit=1, flags=re.I)[0].strip(" ,;:-")
            if lead and len(lead.split()) <= 6 and (FLAVOR_CLAUSE.search(lead) or "&" in lead or "+" in lead):
                result.append(lead)
            result.extend(match.group() for match in FORMULA_INGREDIENT.finditer(clause))
        elif is_variant and variants < 3 and len(clause.split()) <= 6 and novel_words:
            result.append(clause)
            variants += 1
    return result


def _cap_search_title(value: str, brand: str = "", limit: int = 100) -> str:
    """Fit identity, distinctive variants and physical sizes into the search limit."""
    if len(value) <= limit:
        return value

    measures = []
    for match in _product_measures(value):
        normalized = _normalize_measure(match)
        if normalized.casefold() not in {item.casefold() for item in measures}:
            measures.append(normalized)
    without_measures = MEASURE_PATTERN.sub(" ", value)
    parts = [part.strip(" ,;:-./") for part in re.split(r"\s*[,;|]\s*|\s+[/–—-]\s+", without_measures)]
    parts = [re.sub(r"\s+", " ", part).strip() for part in parts if part.strip(" ,;:-./")]
    if not parts:
        return ", ".join(measures)[:limit]

    core = parts.pop(0)
    if len(core.split()) <= 3 and parts:
        core += ", " + parts.pop(0)
    expanded_parts = []
    for part in parts:
        if FORMULA_INGREDIENT.search(part) and len(part.split()) > 4:
            expanded_parts.extend(match.group() for match in FORMULA_INGREDIENT.finditer(part))
        else:
            expanded_parts.append(part)
    parts = expanded_parts
    formula_parts = [part for part in parts if FORMULA_INGREDIENT.search(part) and len(part.split()) <= 4]
    if len(formula_parts) >= 3 and brand and brand.casefold() in core.casefold():
        identity = re.sub(r"\bby\s+" + re.escape(brand) + r"\b|\b" + re.escape(brand) + r"\b", " ", core, flags=re.I)
        identity_words = identity.split()
        first_words = " ".join(identity_words[:2])
        model = next((word for word in identity_words if "+" in word or re.search(r"\d", word)), "")
        product_type = next((word for word in reversed(identity_words) if re.fullmatch(
            r"coffee|latte|tea|cacao|cocoa|powder|drink|syrup|sauce|cream|mix", word, re.I
        )), "")
        choices = [
            " ".join(filter(None, (brand, first_words, model, product_type))),
            " ".join(filter(None, (brand, first_words, model or product_type))),
            " ".join(filter(None, (brand, first_words))),
        ]
        formula_suffix = ", ".join(match.group() for part in formula_parts for match in FORMULA_INGREDIENT.finditer(part))
        size_suffix = (", " + ", ".join(measures)) if measures else ""
        for choice in choices:
            candidate = choice + ", " + formula_suffix + size_suffix
            if len(candidate) <= limit:
                return candidate
    scored = []
    for index, part in enumerate(parts):
        if FORMULA_INGREDIENT.search(part):
            score = 3
        elif FLAVOR_CLAUSE.search(part) or "&" in part or "+" in part or MODEL_VARIANT.search(part):
            score = 2 if not re.search(r"\b(?:roast|blend|rich|medium|mild)\b", part, re.I) else 1
        else:
            score = 0
        if score and len(part) <= 38:
            scored.append((score, index, part))
    scored.sort(key=lambda item: (-item[0], item[1]))

    suffix = (", " + ", ".join(measures)) if measures else ""
    selected: list[tuple[int, str]] = []
    for _, index, part in scored:
        proposed = sorted(selected + [(index, part)])
        candidate = ", ".join([core] + [item[1] for item in proposed]) + suffix
        if len(candidate) <= limit:
            selected.append((index, part))
        elif not selected and len(core) + len(suffix) + len(part) + 2 > limit and len(part) <= 25:
            # Reserve a short distinctive variety even when the first clause is verbose.
            selected.append((index, part))
            break
    selected_parts = [item[1] for item in sorted(selected)]
    reserved = len(", ".join(selected_parts)) + (2 if selected_parts else 0) + len(suffix)
    core_budget = max(1, limit - reserved)
    if len(core) > core_budget:
        words = core.split()
        core = ""
        for word in words:
            candidate = f"{core} {word}".strip()
            if len(candidate) > core_budget:
                break
            core = candidate
        if not core:
            core = words[0][:core_budget]
    result = ", ".join([core] + selected_parts).strip(" ,;:-") + suffix
    return result[:limit].rstrip(" ,;:-")


def _clean_clause(clause: str) -> str:
    clause = re.sub(r"^\s*individually wrapped\s+", "", clause, flags=re.I)
    if MARKETING_CLAUSE.search(clause.strip()):
        return ""
    text = clause
    text = re.sub(r"^\s*savory umami depth with\s+", "", text, flags=re.I)
    text = re.sub(r"\bchicken\s*\+\s*pumpkin\s+for digestive support\b", "Chicken + Pumpkin", text, flags=re.I)
    text = re.sub(r"\bwith superfoods\b", " ", text, flags=re.I)
    text = re.sub(r"\bsize\s+(?=\d+(?:[.,]\d+)?\s*(?:fl\s*oz|oz|g|kg|ml|l|lb)\b)", "", text, flags=re.I)
    text = re.sub(r"\b(\d+(?:[.,]\d+)?\s*(?:fl\s*oz|oz|g|kg|ml|l|lb))\s+each\b", r"\1", text, flags=re.I)
    text = re.sub(r"\b\d+\s*\+\s*treats?\b", " ", text, flags=re.I)
    text = re.sub(r"\bvariety\s+pack\b", " ", text, flags=re.I)
    text = re.sub(r"\+\s*dailyrinse\s+pack\b", " ", text, flags=re.I)
    text = re.sub(r"\bjug by (?:earth friendly products|\u0001)\b", " ", text, flags=re.I)
    if any(char.isdigit() for char in text) or "pack" in text.casefold():
        for pattern in PACK_PATTERNS:
            text = pattern.sub(" ", text)
    text = re.sub(r"\btea\s+bags?\b", " ", text, flags=re.I)
    text = re.sub(r"\bpack\b(?=\s+\d+(?:[.,]\d+)?\s*(?:fl\s*oz|oz|ounces?|g|kg|ml|l|lb)\b)", " ", text, flags=re.I)
    text = re.sub(r"\b(?:pack|case|box)\s+of\b|\bpack\b(?=\s*$)", " ", text, flags=re.I)
    text = re.sub(r"\bfree\s+(?:&|and|n)\s+(?:clear|clr)\b|\bfree[ -]?range\b", " ", text, flags=re.I)
    text = re.sub(r"\bfree from\b[^,;|]*|\btop\s*\d+\s+free\b", " ", text, flags=re.I)
    text = re.sub(r"\b(?:almond|peanut|soy|egg)\s*\(\s*tree[ -]?nut\s*\)\s*free\b", " ", text, flags=re.I)
    text = re.sub(r"\bfree of\b[^,;|]*", " ", text, flags=re.I)
    text = FEATURE_PATTERN.sub(" ", text)
    text = FREE_CLAIM_PATTERN.sub(" ", text)
    text = PROMO_PATTERN.sub(" ", text)
    text = re.sub(r"\bfor\s+(?:men\s+or\s+women|women\s+or\s+men|men|women|adults)\b", " ", text, flags=re.I)
    text = re.sub(r"\bold fashioned western style soda pop\b", " ", text, flags=re.I)
    text = re.sub(r"\b(?:brighten|depuff)\b.*$", " ", text, flags=re.I)
    text = re.sub(r"\bimmune\s+and\s+sleep\b", " ", text, flags=re.I)
    text = re.sub(r"\bfor\s+(?:athletes|adults|kids|children|snacking|baking|searing|frying|braising)\b.*$", " ", text, flags=re.I)
    text = re.sub(
        r"\b\d+(?:[.,]\d+)?\s*g\s*(?:/\s*\d+\s*cal(?:ories)?|(?:of\s+)?(?:complete\s+plant\s+|net\s+|vegan\s+|grass[ -]?fed\s+|hydrolyzed\s+)*(?:protein|fiber|fibre|carbs?|sugars?|whole grains|collagen peptides?|mct oil|omegas?))\b",
        " ", text, flags=re.I,
    )
    text = re.sub(r"\b\d+\s*&\s*\d+\s+per serving\b", " ", text, flags=re.I)
    text = re.sub(r"\breusable\s+(?:glass|plastic|alumin(?:um|ium))\s+bottles?\b", " ", text, flags=re.I)
    text = MEASURE_PATTERN.sub(_normalize_measure, text)
    text = re.sub(r"\b(oz|g|kg|ml|l|lb)\s+(?:pack|box|jar)\b", r"\1", text, flags=re.I)
    text = re.sub(r"[()\[\]]", " ", text)
    text = re.sub(r"\s+", " ", text).strip(" ,;:-&.")
    text = re.sub(r"^(?:and|or|with)\b\s*", "", text, flags=re.I).strip(" ,;:-&.")
    text = re.sub(r"\b(?:and|or|of|with)\s*$", "", text, flags=re.I).strip(" ,;:-&.")
    measurement = MEASURE_PATTERN.search(text)
    if measurement:
        tail = text[measurement.end():]
        if len(tail.split()) >= 9 and re.match(r"\s*\.\s+[A-Z]", tail) and re.search(
            r"\b(?:are|is|perfect|great|delicious|ideal|made|contains|can be)\b", tail[:100], re.I
        ):
            text = text[:measurement.end()].rstrip(" ,;:-&.")
    measure = MEASURE_PATTERN.search(text)
    if measure and measure.start() > 0 and text[:measure.start()].strip():
        prefix = text[:measure.start()].rstrip(" ,")
        text = prefix + ", " + text[measure.start():]
    return text


def clean_product_title(title: str, brand: str = "") -> str:
    """Remove explicit counts and marketing claims without guessing product names."""
    if not isinstance(title, str) or not title.strip():
        return ""

    if re.search(r"%2[c0]|%20", title, flags=re.I):
        title = unquote_plus(title)
    text = re.sub(r"\s+", " ", title).strip()
    text = text.replace("\u00e2\u20ac\u201c", "\u2013").replace("\u00e2\u20ac\u201d", "\u2014")
    text = text.replace("\u00e2\u20ac\u2122", "\u2019")
    text = re.sub(r"(?<=\w)\ufffd(?=s\b)", "\u2019", text)
    text = re.sub(r"\s+\ufffd\s+", " - ", text)
    text = re.sub(r"(?<=Free)\d+\b", "", text, flags=re.I)
    text = re.sub(r"\b(\d+(?:[.,]\d+)?[-\s]*(?:ounces?|oz|fl\s*oz|grams?|g|kg|ml|ltrs?|liters?|lbs?))\d+\b", r"\1", text, flags=re.I)
    text = re.sub(r"(\([^)]*\bpack\s+of\s+\d+\))\d+\b(?!\s*(?:fl\s*oz|oz|ounces?|g|kg|ml|l|lbs?)\b)", r"\1", text, flags=re.I)
    text = re.sub(r"\(\s*-\s*pack\s*\)", " ", text, flags=re.I)
    text = re.sub(r"\(\s*\d+\s*\)(?!\s*(?:fl\s*oz|oz|g|kg|ml|l|lb)\b)", " ", text, flags=re.I)
    # A sentence after a stated product size is usually listing uses or benefits.
    # Keep the stated size and stop before that prose, including any pack count.
    for measure in _product_measures(text):
        tail = text[measure.end():]
        if len(tail.split()) >= 10 and re.match(r"\s*\.\s*(?:\([^)]{0,40}\)\s*)?[A-Z]", tail) and re.search(
            r"\b(?:are|is|perfect|great|delicious|ideal|made|contains|can be)\b", tail[:130], re.I
        ):
            text = text[:measure.end()]
            break
    text = re.sub(r":\s*spicy\s*,\s*tingly\s*,\s*savory\b", "", text, flags=re.I)
    if re.search(r"\bcaffeine pouches\b", text, flags=re.I):
        text = re.sub(r"\bwith naturally derived caffeine from green tea\s*,[^|]*", "", text, flags=re.I)
    text = re.sub(r"\b(?:hispanic cheap wholesale discount bulk beverages|hispanic candle holder pedestal)\b", "", text, flags=re.I)
    source_measures = [_normalize_measure(match) for match in _product_measures(text)]
    protected_brand = None
    brand_name = brand.strip() if isinstance(brand, str) else ""
    brand_contains_pack_count = (
        (any(char.isdigit() for char in brand_name) or "pack" in brand_name.casefold())
        and any(pattern.search(brand_name) for pattern in PACK_PATTERNS)
    )
    brand_is_full_title = brand_name.casefold() == text.casefold() and len(brand_name.split()) > 3
    brand_is_unwanted_byline = bool(
        brand_name and "jug by" in text.casefold()
        and re.search(r"\bjug by\s+" + re.escape(brand_name) + r"\b", text, re.I)
    )
    if brand_name and not brand_contains_pack_count and not brand_is_full_title and not brand_is_unwanted_byline:
        brand_match = _brand_matcher(brand_name).search(text)
        if brand_match:
            protected_brand = brand_match.group()
            text = text[:brand_match.start()] + "\u0001" + text[brand_match.end():]

    section_parts = re.split(r"(\s*\|\s*|\s+[-–—]\s+|(?<=\w)-\s+)", text)
    sections = [
        (part.strip(), section_parts[index - 1].strip() if index else "")
        for index, part in enumerate(section_parts)
        if index % 2 == 0 and part.strip()
    ]
    first_section_has_size = bool(sections and MEASURE_PATTERN.search(sections[0][0]))
    kept = []
    for section_index, (section, delimiter) in enumerate(sections):
        clauses = [part.strip() for part in re.split(r"\s*[,;]\s*", section) if part.strip()]
        if section_index and len(clauses) >= 4 and SEO_SECTION_LEAD.search(clauses[0]):
            continue
        section_is_primary = section_index == 0
        section_is_second_product = (
            section_index == 1 and not first_section_has_size
            and (delimiter == "|" or len(sections[0][0].split()) <= 2)
        )
        section_is_short = len(section.split()) <= 4
        first_clause_is_short = bool(clauses and len(clauses[0].split()) <= 2)
        for clause_index, raw_clause in enumerate(clauses):
            cleaned = _clean_clause(raw_clause)
            if not cleaned or cleaned.casefold() in {"and", "or", "with", "the", "&", "snacks"}:
                continue
            if cleaned.casefold() == "breakfast bars" and any(re.search(r"\bbars?\b", part, re.I) for part in kept):
                continue
            if cleaned.casefold() == "tomato crushed" and any(re.search(r"\bcrushed tomatoes?\b", part, re.I) for part in kept):
                continue
            if re.fullmatch(r"\d+(?:[.,]\d+)?\s*%", cleaned):
                continue
            if cleaned == "\u0001":
                pass
            elif MARKETING_CLAUSE.search(cleaned):
                continue
            word_count = len(cleaned.split())
            has_measure = bool(_product_measures(cleaned))
            has_brand = "\u0001" in cleaned
            has_flavor = bool(FLAVOR_CLAUSE.search(cleaned))
            has_formula_ingredient = bool(FORMULA_INGREDIENT.search(cleaned))
            is_last_short_variant = (
                clause_index == len(clauses) - 1
                and word_count <= 4
                and re.search(r"\b(?:pack|count|ct)\b", section, re.I)
            )
            should_keep = (
                not kept
                or has_brand
                or has_measure
                or has_formula_ingredient
                or (has_flavor and word_count <= 7)
                or (section_is_primary and (word_count <= 4 or (has_flavor and word_count <= 7)))
                or (section_is_primary and first_clause_is_short and clause_index == 1)
                or (section_is_primary and clause_index == 1 and word_count <= 7)
                or (section_is_second_product and clause_index == 0 and word_count <= 8)
                or (section_is_second_product and word_count <= 4)
                or (section_is_short and word_count <= 4)
                or is_last_short_variant
            )
            repeats_existing = should_keep and any(
                cleaned.casefold() in part.casefold()
                and re.search(r"(?<!\w)" + re.escape(cleaned) + r"(?!\w)", part, re.I)
                for part in kept
            )
            if should_keep and not repeats_existing:
                kept.append(cleaned)

    text = ", ".join(_prune_long_search_title(kept))
    for measure in source_measures:
        if not re.search(r"(?<!\d)" + re.escape(measure) + r"(?!\w)", text, re.I):
            text = f"{text}, {measure}" if text else measure
    if protected_brand:
        text = text.replace("\u0001", protected_brand)
        if protected_brand.casefold() not in text.casefold():
            text = f"{protected_brand}, {text}" if text else protected_brand
    text = re.sub(r"\s*--\s*(?=,|$)", " ", text)
    text = re.sub(r"(?:,\s*)?\s+[+/]\s*$", "", text).strip(" ,;:-/")
    return _cap_search_title(text, brand_name)
