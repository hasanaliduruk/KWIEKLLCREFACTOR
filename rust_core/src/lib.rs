use pyo3::prelude::*;
use pyo3::types::PyAny;
use rayon::prelude::*;
use calamine::{open_workbook_auto, Data, Reader};
use rust_xlsxwriter::Workbook;
use serde_json::Value;
use std::path::Path;
use std::sync::atomic::{AtomicUsize, Ordering};
use rustc_hash::FxHashMap;

fn get_col_idx(headers: &[String], possible_names: Option<&Vec<Value>>) -> Result<usize, String> {
    let names = possible_names.ok_or("Ayarlarda sütun listesi eksik.")?;
    for val in names {
        if let Some(name) = val.as_str() {
            if let Some(idx) = headers.iter().position(|h| h.eq_ignore_ascii_case(name)) {
                return Ok(idx);
            }
        }
    }
    Err(format!("Beklenen sütunlardan hiçbiri bulunamadı: {:?}", names))
}

fn clean_upc(cell: &Data) -> String {
    let s = cell.to_string();
    let s = s.trim();
    if let Ok(num) = s.parse::<f64>() {
        if num.fract() == 0.0 {
            return format!("{:.0}", num);
        } else {
            return format!("{}", num);
        }
    }
    s.to_string()
}

struct ParsedRow {
    upc: String,
    price: f64,
    brand: String,
    case: String,
    qty: Option<f64>,
    modified_row: Vec<String>,
}

#[pyfunction]
pub fn process_restock(
    py: Python,
    log_callback: Py<PyAny>,
    ham_files: Vec<String>,
    export_files: Vec<String>,
    restock_files: Vec<String>,
    do_export: bool,
    do_restock: bool,
    save_name: String,
    output_folder: String,
    settings_json: String,
) -> PyResult<String> {
    // 1. JSON String'ini Parse Etme Düzeltmesi
    let settings: Value = serde_json::from_str(&settings_json)
        .map_err(|e| pyo3::exceptions::PyValueError::new_err(format!("JSON Parse Hatası: {}", e)))?;

    py.detach(move || -> PyResult<String> {
        let columns = settings.get("columns").and_then(|v| v.as_object()).ok_or_else(|| pyo3::exceptions::PyValueError::new_err("Columns ayarı eksik."))?;
        let deposits = settings.get("deposits").and_then(|v| v.as_object()).ok_or_else(|| pyo3::exceptions::PyValueError::new_err("Deposits ayarı eksik."))?;

        if do_export && export_files.is_empty() {
            return Err(pyo3::exceptions::PyValueError::new_err("Export işlemi seçildi ancak export dosyaları eksik."));
        }

        let target_results_dir = Path::new(&output_folder).join("sonuclar");
        std::fs::create_dir_all(&target_results_dir).map_err(|e| pyo3::exceptions::PyIOError::new_err(e.to_string()))?;

        let mut export_data: FxHashMap<String, FxHashMap<String, Option<f64>>> = FxHashMap::default();
        if do_export {
            Python::try_attach(|py| -> PyResult<()> {
                log_callback.call1(py, ("Export Verileri Hafızaya alınıyor...", 5))?;
                Ok(())
            }).unwrap()?;
            
            for exp_file in &export_files {
                let prefix = Path::new(exp_file).file_stem().unwrap().to_string_lossy().split('-').next().unwrap_or("").to_string();
                let mut wb = open_workbook_auto(exp_file).map_err(|e| pyo3::exceptions::PyIOError::new_err(e.to_string()))?;
                let sheet = wb.sheet_names().first().unwrap().clone();
                let range = wb.worksheet_range(&sheet).map_err(|e| pyo3::exceptions::PyIOError::new_err(e.to_string()))?;
                
                let row_count = range.get_size().0;
                let mut iter = range.rows();
                
                let header = iter.next().ok_or_else(|| pyo3::exceptions::PyValueError::new_err("Export başlığı bulunamadı."))?;
                let headers: Vec<String> = header.iter().map(|c| c.to_string().trim().to_string()).collect();

                let e_upc_idx = get_col_idx(&headers, columns.get("upc").and_then(|v| v.as_array())).map_err(|e| pyo3::exceptions::PyValueError::new_err(e))?;
                let e_qty_idx = get_col_idx(&headers, columns.get("Quantity on hand").and_then(|v| v.as_array())).map_err(|e| pyo3::exceptions::PyValueError::new_err(e))?;

                let mut qty_map = FxHashMap::default();
                qty_map.reserve(row_count); 
                
                for row in iter {
                    let upc = clean_upc(row.get(e_upc_idx).unwrap_or(&Data::Empty));
                    let qty: Option<f64> = row.get(e_qty_idx).unwrap_or(&Data::Empty).to_string().parse::<f64>().ok();
                    if !upc.is_empty() { qty_map.insert(upc, qty); }
                }
                export_data.insert(prefix, qty_map);
            }
        }

        Python::try_attach(|py| -> PyResult<()> {
            log_callback.call1(py, ("Ham dosyalar paralel işleniyor...", 10))?;
            Ok(())
        }).unwrap()?;

        let processed_count = AtomicUsize::new(0);
        let total_files = ham_files.len();

        let parsed_results_res: Result<Vec<_>, String> = ham_files.par_iter().enumerate().map(|(priority, file_path)| {
            Python::try_attach(|py| -> PyResult<()> {
                log_callback.call1(py, ("", None::<i32>))?;
                Ok(())
            }).unwrap().map_err(|e| e.to_string())?;

            let file_name = Path::new(file_path).file_name().unwrap_or_default().to_string_lossy().to_string();
            let prefix = Path::new(file_path).file_stem().unwrap().to_string_lossy().split('-').next().unwrap_or("").to_string();

            let mut wb = open_workbook_auto(file_path).map_err(|e| format!("{}: {}", file_name, e))?;
            let sheet = wb.sheet_names().first().unwrap().clone();
            let range = wb.worksheet_range(&sheet).map_err(|e| format!("{}: {}", file_name, e))?;
            
            let row_count = range.get_size().0;
            let mut iter = range.rows();
            
            let header_row = iter.next().ok_or(format!("{}: Row başlığı bulunamadı.", file_name))?;
            let mut headers: Vec<String> = header_row.iter().map(|c| c.to_string().trim().to_string()).collect();
            
            let r_upc_idx = get_col_idx(&headers, columns.get("upc").and_then(|v| v.as_array()))?;
            let r_price_idx = get_col_idx(&headers, columns.get("price").and_then(|v| v.as_array()))?;
            let r_brand_idx = get_col_idx(&headers, columns.get("brand").and_then(|v| v.as_array())).ok();
            let r_case_idx = get_col_idx(&headers, columns.get("case").and_then(|v| v.as_array())).ok();
            let r_qty_idx = get_col_idx(&headers, columns.get("Quantity on hand").and_then(|v| v.as_array())).ok();
            
            let mut insert_idx = headers.len();
            if do_export {
                insert_idx = std::cmp::min(headers.len(), r_price_idx + 1);
                headers.insert(insert_idx, "Qty on Hand".to_string());
            }

            let qty_map = export_data.get(&prefix);
            let mut parsed_list = Vec::with_capacity(row_count);
            
            for row in iter {
                let upc = clean_upc(row.get(r_upc_idx).unwrap_or(&Data::Empty));
                if upc.is_empty() { continue; }

                let final_qty: Option<f64> = if do_export {
                    if let Some(map) = qty_map {
                        if map.contains_key(&upc) {
                            map.get(&upc).and_then(|v| *v)
                        } else {
                            continue;
                        }
                    } else {
                        return Err(format!("Export verisi bulunamadı: {}", prefix));
                    }
                } else {
                    if let Some(idx) = r_qty_idx {
                        row.get(idx).unwrap_or(&Data::Empty).to_string().parse::<f64>().ok()
                    } else { None }
                };

                let price = row.get(r_price_idx).unwrap_or(&Data::Empty).to_string().replace(",", ".").parse::<f64>().unwrap_or(999999.0);
                let brand = if let Some(i) = r_brand_idx { row.get(i).unwrap_or(&Data::Empty).to_string() } else { "".to_string() };
                let case = if let Some(i) = r_case_idx { row.get(i).unwrap_or(&Data::Empty).to_string() } else { "".to_string() };
                
                let mut modified_row: Vec<String> = row.iter().map(|c| c.to_string()).collect();
                if do_export {
                    let qty_str = final_qty.map(|q| q.to_string()).unwrap_or_else(|| "#YOK".to_string());
                    modified_row.insert(insert_idx, qty_str);
                }

                parsed_list.push(ParsedRow { upc, price, brand, case, qty: final_qty, modified_row });
            }

            let count = processed_count.fetch_add(1, Ordering::Relaxed) + 1;
            let progress = 10 + (count as f64 / total_files as f64 * 30.0) as u32;
            
            Python::try_attach(|py| -> PyResult<()> {
                let log_msg = format!("Paralel işlendi: {}", file_name);
                log_callback.call1(py, (log_msg, progress))?;
                Ok(())
            }).unwrap().map_err(|e| e.to_string())?;

            Ok((file_path.clone(), priority, prefix, headers, parsed_list))
        }).collect();

        let mut parsed_results = parsed_results_res.map_err(|e| pyo3::exceptions::PyValueError::new_err(e))?;
        parsed_results.sort_by_key(|(_, priority, _, _, _)| *priority);

        Python::try_attach(|py| -> PyResult<()> { log_callback.call1(py, ("Çakışmalar (Deduplication) hesaplanıyor...", 50))?; Ok(()) }).unwrap()?;
        
        let mut lowest_prices: FxHashMap<String, (f64, usize, String, String)> = FxHashMap::default();
        
        for (file_path, priority, prefix, _, parsed_list) in &parsed_results {
            for r in parsed_list {
                let current_entry = lowest_prices.entry(r.upc.clone()).or_insert((r.price, *priority, prefix.clone(), file_path.clone()));
                if r.price < current_entry.0 || (r.price == current_entry.0 && *priority < current_entry.1) {
                    *current_entry = (r.price, *priority, prefix.clone(), file_path.clone());
                }
            }
        }

        Python::try_attach(|py| -> PyResult<()> { log_callback.call1(py, ("Ara çıktılar paralel olarak diske yazılıyor...", 60))?; Ok(()) }).unwrap()?;
        
        let write_results: Result<Vec<_>, String> = parsed_results.par_iter().map(|(file_path, _, prefix, headers, parsed_list)| {
            Python::try_attach(|py| -> PyResult<()> { log_callback.call1(py, ("", None::<i32>))?; Ok(()) }).unwrap().map_err(|e| e.to_string())?;

            let file_name = Path::new(file_path).file_name().unwrap().to_string_lossy().to_string();
            let out_path = target_results_dir.join(&file_name);
            let mut out_wb = Workbook::new();

            if do_export {
                let ws_exp = out_wb.add_worksheet();
                ws_exp.set_name("export sonuc").map_err(|e| e.to_string())?;
                for (c, h) in headers.iter().enumerate() {
                    ws_exp.write_string(0, c as u16, h).map_err(|e| e.to_string())?;
                }
                for (r_idx, r) in parsed_list.iter().enumerate() {
                    for (c_idx, cell) in r.modified_row.iter().enumerate() {
                        ws_exp.write_string((r_idx + 1) as u32, c_idx as u16, cell).map_err(|e| e.to_string())?;
                    }
                }
            }

            let ws_dedup = out_wb.add_worksheet();
            ws_dedup.set_name("dusulmus liste").map_err(|e| e.to_string())?;
            for (c, h) in headers.iter().enumerate() {
                ws_dedup.write_string(0, c as u16, h).map_err(|e| e.to_string())?;
            }

            let mut r_idx = 1;
            for r in parsed_list {
                if let Some(winner) = lowest_prices.get(&r.upc) {
                    if &winner.2 == prefix {
                        for (c_idx, cell) in r.modified_row.iter().enumerate() {
                            ws_dedup.write_string(r_idx, c_idx as u16, cell).map_err(|e| e.to_string())?;
                        }
                        r_idx += 1;
                    }
                }
            }

            out_wb.save(&out_path).map_err(|e| e.to_string())?;
            Ok(())
        }).collect();
        
        write_results.map_err(|e| pyo3::exceptions::PyIOError::new_err(e))?;

        if do_restock {
            Python::try_attach(|py| -> PyResult<()> { log_callback.call1(py, ("Ana restock dosyası oluşturuluyor...", 80))?; Ok(()) }).unwrap()?;
            
            struct WinnerData { supplier: String, price: f64, brand: String, case: String, qty: Option<f64> }
            let mut winners_map: FxHashMap<String, WinnerData> = FxHashMap::default();
            let mut pivot_price: FxHashMap<String, FxHashMap<String, f64>> = FxHashMap::default();
            let mut pivot_qty: FxHashMap<String, FxHashMap<String, f64>> = FxHashMap::default();

            let mut file_order = Vec::new();
            let mut ordered_prefixes = Vec::new();

            for (file_path, _, prefix, _, _) in &parsed_results {
                file_order.push(file_path.clone());
                ordered_prefixes.push(prefix.clone());
            }

            for (file_path, _, prefix, _, parsed_list) in &parsed_results {
                for r in parsed_list {
                    pivot_price.entry(r.upc.clone()).or_default().insert(file_path.clone(), r.price);
                    if let Some(q) = r.qty {
                        pivot_qty.entry(r.upc.clone()).or_default().insert(file_path.clone(), q);
                    }

                    if let Some(winner) = lowest_prices.get(&r.upc) {
                        if &winner.2 == prefix {
                            winners_map.insert(r.upc.clone(), WinnerData {
                                supplier: prefix.clone(), price: r.price, brand: r.brand.clone(), case: r.case.clone(), qty: r.qty,
                            });
                        }
                    }
                }
            }

            let main_file = restock_files.first().ok_or_else(|| pyo3::exceptions::PyValueError::new_err("Restock ana dosyası eksik."))?;
            let mut wb = open_workbook_auto(main_file).map_err(|e| pyo3::exceptions::PyIOError::new_err(e.to_string()))?;
            let sheet = wb.sheet_names().first().unwrap().clone();
            let range = wb.worksheet_range(&sheet).map_err(|e| pyo3::exceptions::PyIOError::new_err(e.to_string()))?;
            let mut iter = range.rows();
            
            let header_row = iter.next().ok_or_else(|| pyo3::exceptions::PyValueError::new_err("Restock başlığı yok."))?;
            let mut headers: Vec<String> = header_row.iter().map(|c| c.to_string().trim().to_string()).collect();
            
            let m_upc_idx = get_col_idx(&headers, columns.get("upc").and_then(|v| v.as_array())).map_err(|e| pyo3::exceptions::PyValueError::new_err(e))?;
            let m_pk_idx = get_col_idx(&headers, columns.get("pk").and_then(|v| v.as_array())).map_err(|e| pyo3::exceptions::PyValueError::new_err(e))?;
            
            headers.push("Brand".to_string()); headers.push("Price".to_string());
            headers.push("Maliyet".to_string()); headers.push("Case".to_string());
            for pfx in &ordered_prefixes { headers.push(format!("{} price", pfx)); }
            headers.push("Qty on Hand".to_string());
            for pfx in &ordered_prefixes { headers.push(format!("{} quantity", pfx)); }
            headers.push("suplier".to_string());

            let target_restock_dir = Path::new(&output_folder).join("restock");
            std::fs::create_dir_all(&target_restock_dir).map_err(|e| pyo3::exceptions::PyIOError::new_err(e.to_string()))?;
            let out_path = target_restock_dir.join(format!("{}.xlsx", save_name));
            
            let mut out_wb = Workbook::new();
            let ws = out_wb.add_worksheet();

            for (c, h) in headers.iter().enumerate() { ws.write_string(0, c as u16, h).map_err(|e| pyo3::exceptions::PyIOError::new_err(e.to_string()))?; }

            let mut r_idx = 1;
            for row in iter {
                Python::try_attach(|py| -> PyResult<()> { log_callback.call1(py, ("", None::<i32>))?; Ok(()) }).unwrap()?; // İptal Kontrolü
                let upc = clean_upc(row.get(m_upc_idx).unwrap_or(&Data::Empty));
                
                let winner = match winners_map.get(&upc) {
                    Some(w) => w,
                    None => continue,
                };

                let mut c_idx = 0;
                for cell in row {
                    ws.write_string(r_idx, c_idx, &cell.to_string()).map_err(|e| pyo3::exceptions::PyIOError::new_err(e.to_string()))?; c_idx += 1;
                }

                let pk_str = row.get(m_pk_idx).unwrap_or(&Data::Empty).to_string().replace("PK", "");
                
                let maliyet = if let Some(dep_val) = deposits.get(&winner.supplier).and_then(|v| v.as_f64()) {
                    match pk_str.parse::<f64>() {
                        Ok(pk_val) => (pk_val * winner.price) + dep_val,
                        Err(_) => winner.price,
                    }
                } else {
                    winner.price
                };

                ws.write_string(r_idx, c_idx, &winner.brand).map_err(|e| pyo3::exceptions::PyIOError::new_err(e.to_string()))?; c_idx += 1;
                ws.write_number(r_idx, c_idx, winner.price).map_err(|e| pyo3::exceptions::PyIOError::new_err(e.to_string()))?; c_idx += 1;
                ws.write_number(r_idx, c_idx, maliyet).map_err(|e| pyo3::exceptions::PyIOError::new_err(e.to_string()))?; c_idx += 1;
                ws.write_string(r_idx, c_idx, &winner.case).map_err(|e| pyo3::exceptions::PyIOError::new_err(e.to_string()))?; c_idx += 1;
                
                for file_path in &file_order {
                    if let Some(p) = pivot_price.get(&upc).and_then(|m| m.get(file_path)) { ws.write_number(r_idx, c_idx, *p).map_err(|e| pyo3::exceptions::PyIOError::new_err(e.to_string()))?; } 
                    else { ws.write_string(r_idx, c_idx, "#YOK").map_err(|e| pyo3::exceptions::PyIOError::new_err(e.to_string()))?; }
                    c_idx += 1;
                }
                
                if let Some(q) = winner.qty { ws.write_number(r_idx, c_idx, q).map_err(|e| pyo3::exceptions::PyIOError::new_err(e.to_string()))?; } 
                else { ws.write_string(r_idx, c_idx, "#YOK").map_err(|e| pyo3::exceptions::PyIOError::new_err(e.to_string()))?; }
                c_idx += 1;
                
                for file_path in &file_order {
                    if let Some(q) = pivot_qty.get(&upc).and_then(|m| m.get(file_path)) { ws.write_number(r_idx, c_idx, *q).map_err(|e| pyo3::exceptions::PyIOError::new_err(e.to_string()))?; } 
                    else { ws.write_string(r_idx, c_idx, "#YOK").map_err(|e| pyo3::exceptions::PyIOError::new_err(e.to_string()))?; }
                    c_idx += 1;
                }
                
                ws.write_string(r_idx, c_idx, &winner.supplier).map_err(|e| pyo3::exceptions::PyIOError::new_err(e.to_string()))?;
                r_idx += 1;
            }
            out_wb.save(&out_path).map_err(|e| pyo3::exceptions::PyIOError::new_err(e.to_string()))?;
            Python::try_attach(|py| -> PyResult<()> { log_callback.call1(py, ("Ana dosya başarıyla kaydedildi.", 100))?; Ok(()) }).unwrap()?;
        }

        Ok(output_folder)
    })
}

#[pymodule]
fn rust_core(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(process_restock, m)?)?;
    Ok(())
}