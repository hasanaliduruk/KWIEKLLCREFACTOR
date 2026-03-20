import os
import pandas as pd


def validate_files(input_files, expected_extension):
    if not input_files:
        raise ValueError("Hata: Dönüştürülecek dosya sağlanmadı.")
    for file in input_files:
        if not os.path.exists(file):
            raise FileNotFoundError(f"Hata: Belirtilen dosya bulunamadı -> {file}")
        if not file.lower().endswith(f".{expected_extension}"):
            raise ValueError(
                f"Hata: Geçersiz dosya tipi. Tüm dosyalar '{expected_extension}' olmalıdır -> {file}"
            )


def process_conversion(
    input_files: list,
    output_folder: str,
    input_type: str,
    output_type: str,
    progress_callback=None,
) -> dict:
    if progress_callback:
        progress_callback("Aşama 1: Ön doğrulama yapılıyor...")
    validate_files(input_files, input_type)

    read_funcs = {
        "csv": pd.read_csv,
        "xlsx": pd.read_excel,
        "txt": lambda f: pd.read_table(f, encoding="latin-1", dtype=str),
    }

    target_dir = os.path.join(output_folder, "sonuc_dosyalari")
    os.makedirs(target_dir, exist_ok=True)

    read_func = read_funcs.get(input_type)
    if not read_func:
        raise ValueError(
            f"Mantıksal Hata: Desteklenmeyen girdi formatı -> {input_type}"
        )

    processed_files = []
    for index, file in enumerate(input_files):
        filename = os.path.basename(file)
        if progress_callback:
            progress_callback(
                f"Aşama 2: İşleniyor ({index+1}/{len(input_files)}): {filename}"
            )

        df = read_func(file)
        if input_type != "txt":
            df = df.astype(str)
        df = df.fillna("")

        if input_type == "csv":
            df = df.map(
                lambda x: (
                    str(x).replace(".", ",")
                    if isinstance(x, (str, float)) and x != "0" and x != "0.0"
                    else x
                )
            )

        new_filename = filename.rsplit(".", 1)[0] + f".{output_type}"
        save_path = os.path.join(target_dir, new_filename)

        if output_type == "csv":
            df.to_csv(save_path, index=False, na_rep="")
        elif output_type == "xlsx":
            df.to_excel(save_path, index=False, na_rep="")
        elif output_type == "txt":
            df.to_csv(save_path, sep="\t", index=False, na_rep="")
        else:
            raise ValueError(
                f"Mantıksal Hata: Desteklenmeyen çıktı formatı -> {output_type}"
            )

        processed_files.append(save_path)

    return {
        "status": "success",
        "message": f"{len(processed_files)} dosya başarıyla dönüştürüldü!",
        "output_path": target_dir,
    }
