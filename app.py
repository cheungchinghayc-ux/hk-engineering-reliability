# -*- coding: utf-8 -*-
"""
Hong Kong Engineering Components Reliability & RUL Analysis Web Platform
專為香港工程界（E&M、屋宇裝備、鐵路、供水、工控）設計之組件可靠度與剩餘壽命預測系統
"""
import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import json

# 設置網頁基本參數
st.set_page_config(
    page_title="HK Engineering Reliability & DIF Analysis Platform",
    page_icon="⚙️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 載入 100 款香港工程常見組件數據庫
COMPONENTS_RAW = [
    {
        "id": 1,
        "name_en": "Water-Cooled Centrifugal Chiller",
        "name_zh": "水冷離心式冷水機 (Chiller)",
        "category": "Building Services - HVAC",
        "beta": 2.5,
        "eta": 150000,
        "mttf_hours": 133000,
        "mttf_years": 25,
        "failure_mode": "葉輪磨損、軸承疲勞、雪種洩漏 (Impeller wear, bearing fatigue)",
        "maintenance_strategy": "每年冷媒油分析、大修檢測、震動頻譜監測 (EMSD / ASHRAE 15)",
        "standards": "EMSD BEC / ASHRAE 90.1 / CIBSE Guide M"
    },
    {
        "id": 2,
        "name_en": "Air-Cooled Screw Chiller",
        "name_zh": "風冷螺桿式冷水機",
        "category": "Building Services - HVAC",
        "beta": 2.2,
        "eta": 110000,
        "mttf_hours": 97400,
        "mttf_years": 18,
        "failure_mode": "螺桿轉子咬死、冷凝盤管腐蝕 (Rotor seizure, coil corrosion)",
        "maintenance_strategy": "定期盤管清洗、潤滑油更換、壓力測試",
        "standards": "EMSD BEC / AHRI 550/590"
    },
    {
        "id": 3,
        "name_en": "Cooling Tower Fan & Motor",
        "name_zh": "冷卻水塔風扇及電機",
        "category": "Building Services - HVAC",
        "beta": 2.8,
        "eta": 65000,
        "mttf_hours": 57900,
        "mttf_years": 10,
        "failure_mode": "皮帶斷裂、扇葉疲勞裂紋、電機浸水受潮 (Belt snap, blade fatigue)",
        "maintenance_strategy": "每月檢查皮帶張力與軸承注油、防退伍軍人症清洗 (EMSD CoP WACS)",
        "standards": "EMSD CoP for Water-cooled Air Conditioning Systems"
    },
    {
        "id": 4,
        "name_en": "Primary Chilled Water Pump",
        "name_zh": "一次冷凍水泵 (Primary Pump)",
        "category": "Building Services - HVAC",
        "beta": 2.3,
        "eta": 120000,
        "mttf_hours": 106000,
        "mttf_years": 20,
        "failure_mode": "機械軸封洩漏、葉輪氣蝕 (Mechanical seal leak, cavitation)",
        "maintenance_strategy": "半年一次同軸度校正、震動分析、更換軸封",
        "standards": "ISO 10816-3 / CIBSE Guide M"
    },
    {
        "id": 5,
        "name_en": "Condenser Water Pump",
        "name_zh": "冷卻水泵 (Condenser Pump)",
        "category": "Building Services - HVAC",
        "beta": 2.6,
        "eta": 90000,
        "mttf_hours": 80100,
        "mttf_years": 15,
        "failure_mode": "軸承磨損、水垢沉積磨蝕 (Bearing wear, scaling erosion)",
        "maintenance_strategy": "季度檢查水流壓差、電機絕緣電阻量度",
        "standards": "CIBSE Guide M / BS EN ISO 9906"
    },
    {
        "id": 6,
        "name_en": "Air Handling Unit (AHU) Centrifugal Fan",
        "name_zh": "風櫃離心風機 (AHU Blower)",
        "category": "Building Services - HVAC",
        "beta": 2.1,
        "eta": 100000,
        "mttf_hours": 88600,
        "mttf_years": 15,
        "failure_mode": "皮帶老化打滑、軸承過熱 (Belt slippage, bearing overheat)",
        "maintenance_strategy": "每月皮帶調整、半年動平衡測試",
        "standards": "ASHRAE 62.1 / CIBSE Guide M"
    },
    {
        "id": 7,
        "name_en": "Fan Coil Unit (FCU) Motor",
        "name_zh": "風機盤管電機 (FCU Motor)",
        "category": "Building Services - HVAC",
        "beta": 1.8,
        "eta": 70000,
        "mttf_hours": 62200,
        "mttf_years": 10,
        "failure_mode": "電機繞組燒毀、軸承乾涸異響 (Winding burnout, dry bearing)",
        "maintenance_strategy": "換季濾網清洗、量度運行電流",
        "standards": "IEC 60034 / EMSD BEC"
    },
    {
        "id": 8,
        "name_en": "Variable Air Volume (VAV) Box Actuator",
        "name_zh": "變風量箱風閥致動器 (VAV Actuator)",
        "category": "Building Services - HVAC",
        "beta": 1.5,
        "eta": 80000,
        "mttf_hours": 72300,
        "mttf_years": 12,
        "failure_mode": "內部齒輪掃齒、電位計反饋失靈 (Gear stripping, potentiometer failure)",
        "maintenance_strategy": "季度訊號校正、手動開關測試",
        "standards": "EN 1751 / CIBSE Guide H"
    },
    {
        "id": 9,
        "name_en": "Smoke Extraction Fan",
        "name_zh": "排煙風機 (Smoke Fan - 250°C/2hr)",
        "category": "Building Services - HVAC",
        "beta": 1.3,
        "eta": 180000,
        "mttf_hours": 165000,
        "mttf_years": 25,
        "failure_mode": "長期備用未開導致軸承咬死、耐高溫繞組老化",
        "maintenance_strategy": "按香港消防處要求每月試運轉 (FSD Circular Letters / BS 7346)",
        "standards": "FSD CoP / BS 7346-2 / EN 12101-3"
    },
    {
        "id": 10,
        "name_en": "Staircase Pressurization Fan",
        "name_zh": "防煙樓梯加壓風機",
        "category": "Building Services - HVAC",
        "beta": 1.4,
        "eta": 160000,
        "mttf_hours": 145000,
        "mttf_years": 22,
        "failure_mode": "風壓感應器漂移、電機接觸器氧化 (Pressure sensor drift)",
        "maintenance_strategy": "季度樓梯間門開/關正壓測試 (50 Pa 測試)",
        "standards": "FSD CoP / BS EN 12101-6"
    },
    {
        "id": 11,
        "name_en": "Motorized Fire Damper Actuator",
        "name_zh": "電動防火閘致動器 (Fire Damper Actuator)",
        "category": "Building Services - HVAC",
        "beta": 1.2,
        "eta": 90000,
        "mttf_hours": 84600,
        "mttf_years": 15,
        "failure_mode": "彈簧疲勞失效、熔斷片斷路、機械阻滯 (Spring fatigue)",
        "maintenance_strategy": "年度消防聯鎖聯動跳閘測試、手動復位",
        "standards": "FSD CoP / BS 9999 / UL 555S"
    },
    {
        "id": 12,
        "name_en": "Plate Heat Exchanger",
        "name_zh": "板式熱交換器 (PHE)",
        "category": "Building Services - HVAC",
        "beta": 2.4,
        "eta": 120000,
        "mttf_hours": 106400,
        "mttf_years": 18,
        "failure_mode": "EPDM 密封墊圈老化硬化、板片水垢結垢結垢沉積堵塞",
        "maintenance_strategy": "年度CIP化學清洗、壓差監測、打壓檢漏",
        "standards": "ASME Sec VIII / BS EN 378"
    },
    {
        "id": 13,
        "name_en": "Semi-Hermetic Screw Compressor",
        "name_zh": "半封閉螺桿式壓縮機",
        "category": "Building Services - HVAC",
        "beta": 2.6,
        "eta": 95000,
        "mttf_hours": 84600,
        "mttf_years": 15,
        "failure_mode": "軸承磨損、滑閥調節卡滯 (Slide valve stuck)",
        "maintenance_strategy": "按運行小時定時大修更換滾針軸承",
        "standards": "ISO 917 / AHRI 500"
    },
    {
        "id": 14,
        "name_en": "Variable Refrigerant Flow (VRF) Outdoor Unit",
        "name_zh": "變頻多聯機室外機 (VRF Inverter)",
        "category": "Building Services - HVAC",
        "beta": 1.9,
        "eta": 85000,
        "mttf_hours": 75400,
        "mttf_years": 12,
        "failure_mode": "變頻器IGBT模組擊穿、四通閥卡死 (Inverter failure)",
        "maintenance_strategy": "散熱翅片高壓清洗、PCB板除塵與電壓檢測",
        "standards": "AHRI 1230 / EMSD BEC"
    },
    {
        "id": 15,
        "name_en": "Expansion Tank Diaphragm",
        "name_zh": "空調密閉膨脹水缸膜片",
        "category": "Building Services - HVAC",
        "beta": 2.7,
        "eta": 70000,
        "mttf_hours": 62300,
        "mttf_years": 10,
        "failure_mode": "丁基橡膠隔膜破裂破穿、氣室預充氮氣洩漏",
        "maintenance_strategy": "每半年檢查預充氣壓、排水觀察是否有水溢出",
        "standards": "BS EN 13831"
    },
    {
        "id": 16,
        "name_en": "Chemical Water Treatment Dosing Pump",
        "name_zh": "循環水化學加藥泵 (Dosing Pump)",
        "category": "Building Services - HVAC",
        "beta": 2.0,
        "eta": 50000,
        "mttf_hours": 44300,
        "mttf_years": 7,
        "failure_mode": "隔膜老化破損、單向止回閥球堵塞 (Check valve clog)",
        "maintenance_strategy": "每月檢查加藥量、更換隔膜組件",
        "standards": "EMSD CoP WACS / CIBSE TM13"
    },
    {
        "id": 17,
        "name_en": "Chilled Water Modulating 2-Way Control Valve",
        "name_zh": "冷凍水比例積分雙通調節閥",
        "category": "Building Services - HVAC",
        "beta": 1.7,
        "eta": 85000,
        "mttf_hours": 75800,
        "mttf_years": 12,
        "failure_mode": "閥桿密封件洩漏、閥芯受氣蝕雜質卡阻",
        "maintenance_strategy": "定期開度行程校準、更換填料密封環",
        "standards": "IEC 60534 / BS 7350"
    },
    {
        "id": 18,
        "name_en": "Differential Pressure (DP) Sensor across Filter",
        "name_zh": "風櫃空氣過濾網壓差開關 (DP Switch)",
        "category": "Building Services - HVAC",
        "beta": 1.4,
        "eta": 90000,
        "mttf_hours": 81900,
        "mttf_years": 12,
        "failure_mode": "膜片老化失去彈性、引壓管積灰堵塞 (Clogged tube)",
        "maintenance_strategy": "吹掃引壓管、用微壓計校正設定動作點",
        "standards": "EN 779 / ISO 16890"
    },
    {
        "id": 19,
        "name_en": "Ventilation Air Louver Actuator",
        "name_zh": "通風百葉電動開關致動器",
        "category": "Building Services - HVAC",
        "beta": 1.5,
        "eta": 75000,
        "mttf_hours": 67800,
        "mttf_years": 12,
        "failure_mode": "露天連桿生銹卡死、電機減速箱齒輪損壞",
        "maintenance_strategy": "連桿注黃油潤滑、防水膠圈檢查",
        "standards": "CIBSE Guide B"
    },
    {
        "id": 20,
        "name_en": "Duct Electric Air Heater (Heater Bank)",
        "name_zh": "風管電加熱器 (Heater Element)",
        "category": "Building Services - HVAC",
        "beta": 2.1,
        "eta": 60000,
        "mttf_hours": 53100,
        "mttf_years": 10,
        "failure_mode": "電熱絲局部過熱氧化熔斷、超溫保護開關觸點黏連",
        "maintenance_strategy": "每年量度冷態/熱態絕緣電阻、高溫斷路保護測試",
        "standards": "BS EN 60335-2-30 / EMSD CoP"
    },
    {
        "id": 21,
        "name_en": "Cast Resin Dry-Type Distribution Transformer",
        "name_zh": "乾式環氧樹脂變壓器 (11kV/380V)",
        "category": "Electrical & Power",
        "beta": 2.2,
        "eta": 250000,
        "mttf_hours": 221000,
        "mttf_years": 30,
        "failure_mode": "絕緣樹脂熱老化局部放電、溫控PT100探頭故障",
        "maintenance_strategy": "年度紅外線熱成像檢查、除塵、局部放電(PD)測試",
        "standards": "IEC 60076-11 / CLP / HKE Supply Rules"
    },
    {
        "id": 22,
        "name_en": "Oil-Immersed Power Transformer",
        "name_zh": "油浸式電力變壓器 (132kV/11kV)",
        "category": "Electrical & Power",
        "beta": 2.4,
        "eta": 280000,
        "mttf_hours": 248000,
        "mttf_years": 35,
        "failure_mode": "絕緣油介電常數劣化、瓦斯繼電器動作、繞組變形",
        "maintenance_strategy": "定期油中溶解氣體分析 (DGA)、微水含量檢測",
        "standards": "IEC 60076 / IEEE C57.104"
    },
    {
        "id": 23,
        "name_en": "11kV Vacuum Circuit Breaker (VCB)",
        "name_zh": "11千伏真空斷路器 (VCB)",
        "category": "Electrical & Power",
        "beta": 1.9,
        "eta": 180000,
        "mttf_hours": 159000,
        "mttf_years": 25,
        "failure_mode": "真空泡真空度下降滅弧失效、分合閘操動機構彈簧卡死",
        "maintenance_strategy": "真空度耐壓測試、分合閘時間同期性量度、機械注脂",
        "standards": "IEC 62271-100 / EMSD COP"
    },
    {
        "id": 24,
        "name_en": "Low Voltage Air Circuit Breaker (ACB)",
        "name_zh": "低壓空氣斷路器 (ACB, 大掣)",
        "category": "Electrical & Power",
        "beta": 2.1,
        "eta": 160000,
        "mttf_hours": 141000,
        "mttf_years": 20,
        "failure_mode": "滅弧罩受損、主觸頭燒蝕氧化、電子脫扣單元(ETU)漂移",
        "maintenance_strategy": "年度主觸頭接觸電阻測試、二次注入繼電保護校驗 (EMSD WR2 周期檢驗)",
        "standards": "BS EN 60947-2 / EMSD CoP (Electricity)"
    },
    {
        "id": 25,
        "name_en": "Moulded Case Circuit Breaker (MCCB)",
        "name_zh": "塑殼斷路器 (MCCB)",
        "category": "Electrical & Power",
        "beta": 1.7,
        "eta": 150000,
        "mttf_hours": 133000,
        "mttf_years": 20,
        "failure_mode": "雙金屬片熱脫扣特性漂移、機構疲勞",
        "maintenance_strategy": "紅外線接頭測溫、緊固接線扭力檢測",
        "standards": "IEC 60947-2 / BS EN 60947-2"
    },
    {
        "id": 26,
        "name_en": "Miniature Circuit Breaker (MCB)",
        "name_zh": "微型斷路器 (MCB, 掣位)",
        "category": "Electrical & Power",
        "beta": 1.5,
        "eta": 140000,
        "mttf_hours": 126000,
        "mttf_years": 20,
        "failure_mode": "接線端子過熱燒焦、內部磁脫扣卡阻",
        "maintenance_strategy": "定期目測與熱成像檢查",
        "standards": "BS EN 60898-1"
    },
    {
        "id": 27,
        "name_en": "Residual Current Device (RCD / RCCB)",
        "name_zh": "漏電斷路器 (RCD / 水氣掣)",
        "category": "Electrical & Power",
        "beta": 1.6,
        "eta": 100000,
        "mttf_hours": 89000,
        "mttf_years": 15,
        "failure_mode": "脫扣機構生銹卡阻、零序互感器磁芯飽和失靈",
        "maintenance_strategy": "每季按壓測試掣 (Test Button)、儀表測量跳脫時間與電流",
        "standards": "BS EN 61008-1 / EMSD CoP"
    },
    {
        "id": 28,
        "name_en": "Automatic Transfer Switch (ATS)",
        "name_zh": "自動轉換開關 (ATS)",
        "category": "Electrical & Power",
        "beta": 1.8,
        "eta": 130000,
        "mttf_hours": 115000,
        "mttf_years": 20,
        "failure_mode": "微動開關輔助觸點失靈、機械互鎖桿變形卡死",
        "maintenance_strategy": "定期市電/發電機切換無載及帶載測試",
        "standards": "IEC 60947-6-1 / NFPA 110"
    },
    {
        "id": 29,
        "name_en": "Emergency Diesel Generator Set",
        "name_zh": "緊急柴油發電機組 (發電機)",
        "category": "Electrical & Power",
        "beta": 1.5,
        "eta": 120000,
        "mttf_hours": 107000,
        "mttf_years": 25,
        "failure_mode": "起動鉛酸電池電壓不足、噴油嘴積碳堵塞、冷卻水套漏水",
        "maintenance_strategy": "每月試機運轉30分鐘、年度假負載 (Dummy Load) 100%負載測試",
        "standards": "FSD CoP / ISO 8528 / NFPA 110"
    },
    {
        "id": 30,
        "name_en": "Uninterruptible Power Supply (UPS) Static Inverter",
        "name_zh": "不斷電系統靜態逆變器 (UPS Inverter)",
        "category": "Electrical & Power",
        "beta": 2.3,
        "eta": 90000,
        "mttf_hours": 79800,
        "mttf_years": 12,
        "failure_mode": "直流濾波電解電容鼓包乾涸、冷卻風扇停轉導致IGBT過熱",
        "maintenance_strategy": "每5年預防性更換直流電容組及散熱風扇",
        "standards": "IEC 62040-3 / IEEE Gold Book"
    },
    {
        "id": 31,
        "name_en": "Valve Regulated Lead-Acid (VRLA) Battery Bank",
        "name_zh": "閥控密封式鉛酸蓄電池組",
        "category": "Electrical & Power",
        "beta": 3.2,
        "eta": 45000,
        "mttf_hours": 40300,
        "mttf_years": 5,
        "failure_mode": "極板硫化、熱失控鼓脹、內阻急劇上升 (Sulfation)",
        "maintenance_strategy": "季度測量單體內阻與浮充電壓、3年一次全容量放電測試",
        "standards": "IEEE 1188 / BS EN 50272-2"
    },
    {
        "id": 32,
        "name_en": "Power Factor Correction Capacitor",
        "name_zh": "功率因數補償電容器 (Capacitor Bank)",
        "category": "Electrical & Power",
        "beta": 2.6,
        "eta": 75000,
        "mttf_hours": 66600,
        "mttf_years": 10,
        "failure_mode": "諧波共振過流擊穿、絕緣自愈次數耗盡擊穿短路",
        "maintenance_strategy": "每季檢測運行電流平衡度及熱成像",
        "standards": "IEC 60831 / CLP Supply Rules"
    },
    {
        "id": 33,
        "name_en": "Active Harmonic Filter (AHF)",
        "name_zh": "有源電力濾波器 (AHF)",
        "category": "Electrical & Power",
        "beta": 1.9,
        "eta": 80000,
        "mttf_hours": 71000,
        "mttf_years": 12,
        "failure_mode": "DSP控制板故障、散熱通道積塵過熱報警",
        "maintenance_strategy": "定期清潔濾網、固件升級、諧波畸變率(THDi)監控",
        "standards": "IEEE 519 / IEC 61000-4-30"
    },
    {
        "id": 34,
        "name_en": "Surge Protective Device (SPD)",
        "name_zh": "防雷突波吸收器 (SPD / 避雷器)",
        "category": "Electrical & Power",
        "beta": 1.4,
        "eta": 100000,
        "mttf_hours": 91000,
        "mttf_years": 15,
        "failure_mode": "氧化鋅壓敏電阻 (MOV) 經多次浪涌衝擊性能退化擊穿",
        "maintenance_strategy": "每次雷暴後檢查視窗顏色狀態 (綠色正常/紅色損壞)",
        "standards": "BS EN 62305 / IEC 61643-11"
    },
    {
        "id": 35,
        "name_en": "11kV XLPE Insulated Power Cable",
        "name_zh": "11千伏交聯聚乙烯電力電纜 (XLPE Cable)",
        "category": "Electrical & Power",
        "beta": 2.5,
        "eta": 300000,
        "mttf_hours": 266000,
        "mttf_years": 35,
        "failure_mode": "水樹老化引發電樹局部放電、中間接頭 (Cable Joint) 受潮擊穿",
        "maintenance_strategy": "5年進行一次極低頻 (VLF) 耐壓及介損 (Tan Delta) 測試",
        "standards": "IEC 60502-2 / IEEE 400.2"
    },
    {
        "id": 36,
        "name_en": "Copper Busduct / Busway System",
        "name_zh": "銅母線槽系統 (Busway / Busduct)",
        "category": "Electrical & Power",
        "beta": 1.8,
        "eta": 280000,
        "mttf_hours": 249000,
        "mttf_years": 30,
        "failure_mode": "插接箱接頭受潮生氧化熱阻過大、絕緣夾老化破損",
        "maintenance_strategy": "年度紅外線掃描檢測接頭溫升、螺栓力矩標記檢查",
        "standards": "IEC 61439-6 / BS EN 61439-6"
    },
    {
        "id": 37,
        "name_en": "Protection Current Transformer (CT)",
        "name_zh": "保護用電流互感器 (CT)",
        "category": "Electrical & Power",
        "beta": 1.3,
        "eta": 260000,
        "mttf_hours": 239000,
        "mttf_years": 30,
        "failure_mode": "二次側開路產生高壓燒毀、鐵芯飽和特性變化",
        "maintenance_strategy": "定期伏安特性 (励磁特性) 曲線校測",
        "standards": "IEC 61869-2"
    },
    {
        "id": 38,
        "name_en": "Protection Voltage Transformer (VT)",
        "name_zh": "保護用電壓互感器 (VT)",
        "category": "Electrical & Power",
        "beta": 1.4,
        "eta": 260000,
        "mttf_hours": 237000,
        "mttf_years": 30,
        "failure_mode": "一次側熔斷器熔斷、鐵磁共振擊穿",
        "maintenance_strategy": "年度變比與角差校核、絕緣阻抗量度",
        "standards": "IEC 61869-3"
    },
    {
        "id": 39,
        "name_en": "Earthing & Lightning Rod System",
        "name_zh": "接地極與避雷導體系統",
        "category": "Electrical & Power",
        "beta": 1.2,
        "eta": 250000,
        "mttf_hours": 235000,
        "mttf_years": 30,
        "failure_mode": "土壤化學物質腐蝕接地銅帶、接地電阻超標 (>10 Ohm)",
        "maintenance_strategy": "年度接地電阻搖表量度 (Earth Megger Test) (EMSD WR2 要求)",
        "standards": "EMSD CoP / BS 7430 / BS EN 62305"
    },
    {
        "id": 40,
        "name_en": "Motor Control Centre (MCC) Magnetic Contactor",
        "name_zh": "馬達控制中心電磁接觸器 (Contactor)",
        "category": "Electrical & Power",
        "beta": 2.2,
        "eta": 80000,
        "mttf_hours": 70900,
        "mttf_years": 10,
        "failure_mode": "銀合金觸點電弧燒蝕焊死、吸持線圈過熱燒毀",
        "maintenance_strategy": "每半年檢查觸點厚度、清除電弧煙垢、測量線圈電阻",
        "standards": "IEC 60947-4-1"
    },
    {
        "id": 41,
        "name_en": "Potable Water Hydro-Pneumatic Booster Pump",
        "name_zh": "食水變頻增壓水泵 (Booster Pump)",
        "category": "Plumbing & Drainage",
        "beta": 2.2,
        "eta": 90000,
        "mttf_hours": 79700,
        "mttf_years": 12,
        "failure_mode": "機械密封滴漏、止回閥卡死導致泵頻繁點動",
        "maintenance_strategy": "每月檢查泵體振動與洩漏、變頻恆壓設定校驗 (WSD 要求)",
        "standards": "WSD Handbook / BS EN 806 / CIBSE Guide G"
    },
    {
        "id": 42,
        "name_en": "Submersible Sump Drainage Pump",
        "name_zh": "污水坑沉水泵 (Sump Pump)",
        "category": "Plumbing & Drainage",
        "beta": 2.7,
        "eta": 50000,
        "mttf_hours": 44500,
        "mttf_years": 8,
        "failure_mode": "機械油室入水、電機浸水絕緣擊穿、葉輪被沙石卡死",
        "maintenance_strategy": "季度吊泵檢查油室油質、清理坑底淤泥沉積",
        "standards": "DSD Sewerage Manual / BS EN 12050"
    },
    {
        "id": 43,
        "name_en": "Sewage Grinder / Cutter Pump",
        "name_zh": "污水切割粉碎泵",
        "category": "Plumbing & Drainage",
        "beta": 2.9,
        "eta": 40000,
        "mttf_hours": 35600,
        "mttf_years": 6,
        "failure_mode": "鎢鋼切割刀片磨鈍卡滯、纖維纏繞葉輪",
        "maintenance_strategy": "每半年拆檢研磨或更換刀盤、熱過載繼電器測試",
        "standards": "DSD Practice Notes / BS EN 12050-1"
    },
    {
        "id": 44,
        "name_en": "Direct-Acting Pressure Reducing Valve (PRV)",
        "name_zh": "直接作用式減壓閥 (PRV)",
        "category": "Plumbing & Drainage",
        "beta": 1.9,
        "eta": 75000,
        "mttf_hours": 66500,
        "mttf_years": 10,
        "failure_mode": "調壓彈簧疲勞失準、橡膠膜片老化穿孔、閥座雜質沖刷",
        "maintenance_strategy": "半年一次量度進出口動態/靜態水壓、清洗前置濾網",
        "standards": "WSD Requirements / BS EN 1567"
    },
    {
        "id": 45,
        "name_en": "Pilot-Operated Water PRV",
        "name_zh": "先導式水管減壓閥",
        "category": "Plumbing & Drainage",
        "beta": 2.1,
        "eta": 70000,
        "mttf_hours": 62000,
        "mttf_years": 10,
        "failure_mode": "先導管路針閥被沙石堵塞、主活塞密封圈磨損水錘",
        "maintenance_strategy": "定期通洗銅先導管、校準先導閥彈簧",
        "standards": "AWWA C530 / WSD Standards"
    },
    {
        "id": 46,
        "name_en": "Motorized Butterfly Valve",
        "name_zh": "電動蝶閥 (Motorized Butterfly Valve)",
        "category": "Plumbing & Drainage",
        "beta": 1.7,
        "eta": 80000,
        "mttf_hours": 71200,
        "mttf_years": 12,
        "failure_mode": "EPDM閥座橡膠剝落、電動執行器微動開關限位失效",
        "maintenance_strategy": "每季全行程開關測試、更換EPDM襯裡",
        "standards": "BS EN 593 / ISO 10631"
    },
    {
        "id": 47,
        "name_en": "Ductile Iron Resilient-Seated Gate Valve",
        "name_zh": "球墨鑄鐵彈性座封閘閥",
        "category": "Plumbing & Drainage",
        "beta": 1.5,
        "eta": 130000,
        "mttf_hours": 117000,
        "mttf_years": 20,
        "failure_mode": "閥底沉積泥沙無法全關、閥桿銅螺母脫絲",
        "maintenance_strategy": "每年開關閥門一次以防結垢咬死",
        "standards": "BS EN 1171 / WSD Standard Drawings"
    },
    {
        "id": 48,
        "name_en": "Dual-Plate Wafer Check Valve",
        "name_zh": "雙板對夾式止回閥 (逆止閥)",
        "category": "Plumbing & Drainage",
        "beta": 2.4,
        "eta": 70000,
        "mttf_hours": 62100,
        "mttf_years": 10,
        "failure_mode": "扭轉彈簧斷裂、閥瓣銷軸磨損閉合不及引起水錘",
        "maintenance_strategy": "停泵時監聽有無劇烈水錘碰撞聲、定期檢修彈簧",
        "standards": "API 594 / BS EN 12334"
    },
    {
        "id": 49,
        "name_en": "Automatic Air Release Valve",
        "name_zh": "自動排氣閥 (Air Release Valve)",
        "category": "Plumbing & Drainage",
        "beta": 2.0,
        "eta": 60000,
        "mttf_hours": 53200,
        "mttf_years": 8,
        "failure_mode": "不銹鋼浮球被水垢黏連卡在底部造成漏水、排氣微孔堵塞",
        "maintenance_strategy": "半年拆開清洗浮球與密封面",
        "standards": "AWWA C512 / BS EN 1074-4"
    },
    {
        "id": 50,
        "name_en": "Electromagnetic Water Flow Meter",
        "name_zh": "電磁流量計 (Magflow Meter)",
        "category": "Plumbing & Drainage",
        "beta": 1.6,
        "eta": 110000,
        "mttf_hours": 98000,
        "mttf_years": 15,
        "failure_mode": "測量電極表面附著絕緣污垢水垢、轉換器電源模組擊穿",
        "maintenance_strategy": "定期零點自校、清洗襯裡電極",
        "standards": "ISO 4064 / OIML R49 / WSD Approved"
    },
    {
        "id": 51,
        "name_en": "Ultrasonic Level Transmitter",
        "name_zh": "超聲波液位變送器",
        "category": "Plumbing & Drainage",
        "beta": 1.4,
        "eta": 95000,
        "mttf_hours": 86000,
        "mttf_years": 12,
        "failure_mode": "水坑高濕環境使換能器探頭結露凝結水、假回波干擾",
        "maintenance_strategy": "定期擦拭探頭表面、排除盲區干擾物反射",
        "standards": "IEC 60770 / DSD Guideline"
    },
    {
        "id": 52,
        "name_en": "Mechanical Float Ball Valve",
        "name_zh": "水箱機械浮球閥",
        "category": "Plumbing & Drainage",
        "beta": 2.5,
        "eta": 50000,
        "mttf_hours": 44300,
        "mttf_years": 6,
        "failure_mode": "銅浮球破損進水沉底、活塞密封墊磨損引起水箱溢流",
        "maintenance_strategy": "每月巡視水箱溢流口有無水漏出、更換橡膠平墊",
        "standards": "BS 1212 / WSD Requirements"
    },
    {
        "id": 53,
        "name_en": "Hydro-Pneumatic Pressure Vessel",
        "name_zh": "供水氣壓缸 (Pressure Vessel)",
        "category": "Plumbing & Drainage",
        "beta": 2.3,
        "eta": 75000,
        "mttf_hours": 66400,
        "mttf_years": 10,
        "failure_mode": "內部膠囊疲勞撕裂、缸底受冷凝水銹蝕破穿",
        "maintenance_strategy": "每半年檢查預充壓力、水壓安全閥每年年檢 (Boilers Ordinance)",
        "standards": "Cap 56 Boilers and Pressure Vessels Ordinance"
    },
    {
        "id": 54,
        "name_en": "Ultraviolet (UV) Water Disinfection System",
        "name_zh": "紫外線水質殺菌器 (UV Lamp)",
        "category": "Plumbing & Drainage",
        "beta": 3.0,
        "eta": 12000,
        "mttf_hours": 10700,
        "mttf_years": 1.5,
        "failure_mode": "UV石英汞燈管光強衰減 (<70% 殺菌強度)、石英套管結垢",
        "maintenance_strategy": "每8000-10000小時定時更換燈管、定期機械擦洗套管",
        "standards": "NSF/ANSI 55 / WSD Guidelines"
    },
    {
        "id": 55,
        "name_en": "Reduced Pressure Zone (RPZ) Backflow Preventer",
        "name_zh": "防倒流裝置 (RPZ Valve)",
        "category": "Plumbing & Drainage",
        "beta": 2.2,
        "eta": 55000,
        "mttf_hours": 48700,
        "mttf_years": 8,
        "failure_mode": "中間差壓排泄閥滴漏、止回彈簧附著鐵銹失靈",
        "maintenance_strategy": "按水務署要求每年由持牌水喉匠進行壓差測試",
        "standards": "WSD Circular Letters / BS EN 12729"
    },
    {
        "id": 56,
        "name_en": "Fire Hydrant / Hose Reel Booster Pump",
        "name_zh": "消防栓/喉轆加壓泵 (FH/HR Pump)",
        "category": "Fire Services",
        "beta": 1.5,
        "eta": 150000,
        "mttf_hours": 135000,
        "mttf_years": 25,
        "failure_mode": "長年靜止備用導致軸承/軸封銹死、起動控制櫃接觸器接觸不良",
        "maintenance_strategy": "每月消防試泵跳掣測試、年度消防處FS251保養簽發",
        "standards": "FSD CoP / BS 5306-1 / Cap 95 Fire Services Ordinance"
    },
    {
        "id": 57,
        "name_en": "Automatic Sprinkler System Alarm Valve",
        "name_zh": "自動花灑警報閥組 (Alarm Check Valve)",
        "category": "Fire Services",
        "beta": 1.3,
        "eta": 180000,
        "mttf_hours": 165000,
        "mttf_years": 25,
        "failure_mode": "水力警鈴水輪結垢銹死、減速室小孔堵塞引起誤報警",
        "maintenance_strategy": "每季放水測試水力警鈴轉動、清洗警報管路濾網",
        "standards": "FSD CoP / LPC Rules / BS EN 12845"
    },
    {
        "id": 58,
        "name_en": "Sprinkler Water Flow Switch",
        "name_zh": "花灑水流指示器 (Flow Switch)",
        "category": "Fire Services",
        "beta": 1.6,
        "eta": 90000,
        "mttf_hours": 80700,
        "mttf_years": 15,
        "failure_mode": "微動開關接點氧化失靈、阻尼延時氣囊老化引起誤動",
        "maintenance_strategy": "季度末端試水閥(Inspector Test Valve)放水聯鎖測試",
        "standards": "UL 346 / NFPA 13 / FSD CoP"
    },
    {
        "id": 59,
        "name_en": "Fire Service Inset Breeching Inlet",
        "name_zh": "消防入水口 (Breeching Inlet)",
        "category": "Fire Services",
        "beta": 1.2,
        "eta": 200000,
        "mttf_hours": 188000,
        "mttf_years": 30,
        "failure_mode": "橡膠單向止回瓣硬化漏水、排水考克(Drain Cock)滲漏",
        "maintenance_strategy": "年度打水壓檢測、清洗止回橡膠瓣面",
        "standards": "BS 5041-1 / FSD CoP"
    },
    {
        "id": 60,
        "name_en": "Addressable Optical Smoke Detector",
        "name_zh": "地址碼光電感煙探測器 (Smoke Detector)",
        "category": "Fire Services",
        "beta": 1.8,
        "eta": 80000,
        "mttf_hours": 70900,
        "mttf_years": 10,
        "failure_mode": "迷宮暗室積灰引發假火警誤報 (False alarm)、光電二極管衰減",
        "maintenance_strategy": "定期專用煙霧吹掃測試、定期更換或除塵清潔光學室",
        "standards": "BS EN 54-7 / FSD Circular Letters"
    },
    {
        "id": 61,
        "name_en": "Rate-of-Rise Heat Detector",
        "name_zh": "定溫/差溫感溫探測器 (Heat Detector)",
        "category": "Fire Services",
        "beta": 1.4,
        "eta": 100000,
        "mttf_hours": 91000,
        "mttf_years": 12,
        "failure_mode": "雙金屬片機構疲勞失準、熱敏電阻阻值漂移",
        "maintenance_strategy": "每年抽樣發熱器現場加溫觸發檢驗",
        "standards": "BS EN 54-5 / FSD CoP"
    },
    {
        "id": 62,
        "name_en": "Manual Fire Alarm Call Point (Break-Glass)",
        "name_zh": "手動火警破玻璃按鈕 (Manual Call Point)",
        "category": "Fire Services",
        "beta": 1.1,
        "eta": 140000,
        "mttf_hours": 134000,
        "mttf_years": 20,
        "failure_mode": "微動觸點氧化接觸不良、鑰匙復位機構卡阻",
        "maintenance_strategy": "每月巡檢抽查使用測試鑰匙激活測試",
        "standards": "BS EN 54-11 / FSD CoP"
    },
    {
        "id": 63,
        "name_en": "Fire Alarm Bell / Electronic Sounder",
        "name_zh": "火警警鐘 / 電子聲光報警器",
        "category": "Fire Services",
        "beta": 1.5,
        "eta": 95000,
        "mttf_hours": 85700,
        "mttf_years": 15,
        "failure_mode": "警鐘打錘螺線管線圈燒毀、電子驅動電容爆漿",
        "maintenance_strategy": "消防演習及定期警鐘響鈴測試聲壓級 (>85dBA)",
        "standards": "BS EN 54-3 / FSD CoP"
    },
    {
        "id": 64,
        "name_en": "Fire Alarm Control Panel (FACP) Mainboard",
        "name_zh": "消防主警報控制盤主板 (FACP Board)",
        "category": "Fire Services",
        "beta": 1.6,
        "eta": 110000,
        "mttf_hours": 98600,
        "mttf_years": 15,
        "failure_mode": "環路驅動IC擊穿、備用充電板損壞無法浮充",
        "maintenance_strategy": "每月模擬主電斷電測量蓄電池備用續航 (>24hr)",
        "standards": "BS EN 54-2 / BS EN 54-4"
    },
    {
        "id": 65,
        "name_en": "Clean Agent (FM-200 / Novec 1230) Discharge Nozzle",
        "name_zh": "氣體滅火噴嘴 (Gas Extinguishing Nozzle)",
        "category": "Fire Services",
        "beta": 1.1,
        "eta": 200000,
        "mttf_hours": 192000,
        "mttf_years": 30,
        "failure_mode": "噴嘴孔被粉刷油漆或防塵袋遮擋堵塞",
        "maintenance_strategy": "目測噴嘴角度及孔徑無堵塞、無遮擋物",
        "standards": "NFPA 2001 / ISO 14520 / FSD CoP"
    },
    {
        "id": 66,
        "name_en": "CO2 / Clean Agent Cylinder Release Solenoid",
        "name_zh": "氣體滅火鋼樽電磁釋放閥 (Solenoid Actuator)",
        "category": "Fire Services",
        "beta": 1.4,
        "eta": 80000,
        "mttf_hours": 72800,
        "mttf_years": 12,
        "failure_mode": "電磁線圈受潮短路、撞針彈簧銹死無法刺破銅片",
        "maintenance_strategy": "拆下電磁閥進行離線模擬放氣跳脫試驗",
        "standards": "BS 5306-4 / NFPA 2001"
    },
    {
        "id": 67,
        "name_en": "Self-Contained Emergency Luminaire Inverter",
        "name_zh": "自攜電池應急照明逆變電路板",
        "category": "Fire Services",
        "beta": 2.5,
        "eta": 45000,
        "mttf_hours": 39900,
        "mttf_years": 5,
        "failure_mode": "內置鎳鎘/鋰電池壽命耗盡、逆變驅動模組擊穿",
        "maintenance_strategy": "每月斷電2小時放電測試、年度更換衰減電池 (FSD 條例)",
        "standards": "FSD Circular Letters / BS 5266 / BS EN 1838"
    },
    {
        "id": 68,
        "name_en": "Emergency Exit Sign LED Driver",
        "name_zh": "緊急出路指示燈 LED 驅動器",
        "category": "Fire Services",
        "beta": 2.3,
        "eta": 50000,
        "mttf_hours": 44300,
        "mttf_years": 6,
        "failure_mode": "高溫環境下濾波電容乾涸失常、LED燈珠光衰熄滅",
        "maintenance_strategy": "定期巡視出路標誌常亮狀態與光度檢查",
        "standards": "BS 5499 / FSD CoP"
    },
    {
        "id": 69,
        "name_en": "Motorized Fire Shutter Gearbox Motor",
        "name_zh": "電動防火山捲閘電機及減速箱",
        "category": "Fire Services",
        "beta": 1.6,
        "eta": 75000,
        "mttf_hours": 67200,
        "mttf_years": 12,
        "failure_mode": "剎車抱閘電磁鐵卡阻、熱熔斷片熔斷機構卡死",
        "maintenance_strategy": "每季全行程升降測試、重力自降防墜試驗",
        "standards": "BS 476-22 / FSD CoP"
    },
    {
        "id": 70,
        "name_en": "Kitchen Wet Chemical Extinguishing Actuator",
        "name_zh": "廚房濕式化學滅火系統機械釋放機構",
        "category": "Fire Services",
        "beta": 1.7,
        "eta": 65000,
        "mttf_hours": 57900,
        "mttf_years": 8,
        "failure_mode": "煙罩重油污滲入使滑輪鋼索黏死、易熔合金片感應遲鈍",
        "maintenance_strategy": "每半年清除不銹鋼拉索油垢、更換易熔合金金屬片",
        "standards": "NFPA 17A / FSD Circular Letters"
    },
    {
        "id": 71,
        "name_en": "Permanent Magnet Synchronous Lift Traction Machine",
        "name_zh": "永磁同步無齒輪升降機曳引機 (Traction Machine)",
        "category": "Lift & Escalator",
        "beta": 2.2,
        "eta": 150000,
        "mttf_hours": 132900,
        "mttf_years": 20,
        "failure_mode": "機械制動器(抱閘)摩擦片磨損、曳引輪繩槽磨損 (Sheave wear)",
        "maintenance_strategy": "按機電署每半月一次例行保養、年度由註冊升降機工程師檢驗簽發 Form 11",
        "standards": "EMSD CoP for Lift & Escalator / Cap 618 / EN 81-20"
    },
    {
        "id": 72,
        "name_en": "Lift Variable Voltage Variable Frequency (VVVF) Inverter",
        "name_zh": "升降機變頻變壓器 (VVVF Drive)",
        "category": "Lift & Escalator",
        "beta": 2.1,
        "eta": 80000,
        "mttf_hours": 70800,
        "mttf_years": 10,
        "failure_mode": "電解電容壽命終了、散熱風扇卡死導致IGBT熱穿孔",
        "maintenance_strategy": "定期吸塵清理驅動櫃、檢查電容母線紋波電壓",
        "standards": "EN 81-20 / IEC 61800"
    },
    {
        "id": 73,
        "name_en": "Elevator Car Door Operator Motor & Belt",
        "name_zh": "升降機門機電機及同步帶 (Door Operator)",
        "category": "Lift & Escalator",
        "beta": 2.4,
        "eta": 45000,
        "mttf_hours": 39900,
        "mttf_years": 6,
        "failure_mode": "同步帶打滑齒形磨損、光電門刀感應器位置偏移",
        "maintenance_strategy": "每月檢查門帶張力、清潔地檻滑槽沙石",
        "standards": "EN 81-20 / EMSD CoP"
    },
    {
        "id": 74,
        "name_en": "Lift Steel Wire Suspension Rope",
        "name_zh": "升降機鋼絲懸掛索纜 (Hoist Rope)",
        "category": "Lift & Escalator",
        "beta": 3.1,
        "eta": 60000,
        "mttf_hours": 53700,
        "mttf_years": 8,
        "failure_mode": "鋼絲斷絲超標、直徑磨損變細、麻芯乾涸生銹 (Crown wire break)",
        "maintenance_strategy": "每月鋼絲繩斷絲計數檢測、繩槽落差測量、 Form 11 載重試驗",
        "standards": "ISO 4344 / EMSD CoP / BS EN 12385-5"
    },
    {
        "id": 75,
        "name_en": "Over-Speed Governor & Safety Gear Assembly",
        "name_zh": "限速器及安全鉗裝置 (Governor & Safety Gear)",
        "category": "Lift & Escalator",
        "beta": 1.3,
        "eta": 180000,
        "mttf_hours": 165000,
        "mttf_years": 25,
        "failure_mode": "離心甩塊機械關節缺油銹阻、提拉連桿卡滯",
        "maintenance_strategy": "年度超速打扣動作試驗、每5年滿載下行急停剎車安全鉗試驗 (Form 11)",
        "standards": "EN 81-20 / EN 81-50 / EMSD CoP"
    },
    {
        "id": 76,
        "name_en": "Hydraulic Lift Cylinder & Ram Packing",
        "name_zh": "油壓升降機油缸及柱塞密封圈 (Ram Seal)",
        "category": "Lift & Escalator",
        "beta": 2.6,
        "eta": 70000,
        "mttf_hours": 62200,
        "mttf_years": 10,
        "failure_mode": "柱塞油封聚氨酯老化漏油、缸筒內部拉傷洩壓溜車",
        "maintenance_strategy": "每月檢查柱塞表面光潔度、漏油回收瓶油位",
        "standards": "EN 81-2"
    },
    {
        "id": 77,
        "name_en": "Escalator Main Drive Motor & Worm Gearbox",
        "name_zh": "自動扶梯主驅動電機及蝸輪減速箱",
        "category": "Lift & Escalator",
        "beta": 2.3,
        "eta": 120000,
        "mttf_hours": 106300,
        "mttf_years": 16,
        "failure_mode": "蝸輪青銅齒面磨損間隙增大、主軸承疲勞滾道剝落",
        "maintenance_strategy": "每季度齒輪油油樣檢測、年度剎車力矩及反轉保護測試",
        "standards": "EN 115-1 / EMSD CoP for Escalator"
    },
    {
        "id": 78,
        "name_en": "Escalator Step Chain Link & Bushing",
        "name_zh": "自動扶梯梯級鏈條及銷軸襯套 (Step Chain)",
        "category": "Lift & Escalator",
        "beta": 2.8,
        "eta": 70000,
        "mttf_hours": 62300,
        "mttf_years": 9,
        "failure_mode": "鏈條銷軸磨損導致節距拉長伸長、潤滑不足乾磨發熱",
        "maintenance_strategy": "每月自動加油泵檢查、每半年量度梯級鏈伸長量及下陷監測",
        "standards": "EN 115-1 / EMSD CoP"
    },
    {
        "id": 79,
        "name_en": "Escalator Comb Plate & Safety Switch",
        "name_zh": "扶梯梳齒板及安全聯鎖微動開關 (Comb Plate)",
        "category": "Lift & Escalator",
        "beta": 1.7,
        "eta": 50000,
        "mttf_hours": 44500,
        "mttf_years": 6,
        "failure_mode": "外物卡入導致梳齒斷裂、梳齒微動開關移位失靈",
        "maintenance_strategy": "每週巡視梳齒嚙合深度、每月手動觸發微動保護跳掣測試",
        "standards": "EN 115-1 / EMSD CoP"
    },
    {
        "id": 80,
        "name_en": "Escalator Handrail Drive Friction Wheel & Belt",
        "name_zh": "扶手帶驅動摩擦輪及橡膠帶 (Handrail Drive)",
        "category": "Lift & Escalator",
        "beta": 2.2,
        "eta": 45000,
        "mttf_hours": 39800,
        "mttf_years": 6,
        "failure_mode": "橡膠扶手帶內部鋼絲疲勞斷裂裂紋、驅動輪打滑引起速度不同步",
        "maintenance_strategy": "每月檢查扶手帶表面老化程度、梯級與扶手帶同步速度檢測 (容差 ±2%)",
        "standards": "EN 115-1 / EMSD CoP"
    },
    {
        "id": 81,
        "name_en": "Railway Point Machine (Track Switch Actuator)",
        "name_zh": "鐵路道岔轉轍機 (Point Machine - MTR Spec)",
        "category": "Railway & Transport",
        "beta": 1.9,
        "eta": 120000,
        "mttf_hours": 106500,
        "mttf_years": 15,
        "failure_mode": "密貼接點氧化、滾珠絲杠磨損卡死、表示接點缺口超差",
        "maintenance_strategy": "每季測定轉轍力、表示缺口光電測量、絲杠專用脂加注",
        "standards": "MTR Signalling Standards / BS 7345 / EN 50126"
    },
    {
        "id": 82,
        "name_en": "Audio Frequency Track Circuit Receiver",
        "name_zh": "音頻無絕緣軌道電路接收單元",
        "category": "Railway & Transport",
        "beta": 1.5,
        "eta": 150000,
        "mttf_hours": 135000,
        "mttf_years": 18,
        "failure_mode": "濾波電容漂移使載頻偏移失諧、雷擊感應過電壓擊穿",
        "maintenance_strategy": "定期量度軌面信號感應電壓、調諧單元S帶阻抗檢測",
        "standards": "EN 50129 / MTR Standards"
    },
    {
        "id": 83,
        "name_en": "Axle Counter Wheel Sensor",
        "name_zh": "計軸器車輪電磁傳感頭 (Axle Counter Sensor)",
        "category": "Railway & Transport",
        "beta": 1.6,
        "eta": 110000,
        "mttf_hours": 98700,
        "mttf_years": 14,
        "failure_mode": "軌道強烈震動造成夾具鬆脫位移、傳感線圈磁芯受損",
        "maintenance_strategy": "每月軌道檢測夾具扭力、傳感器殘留電壓校驗",
        "standards": "EN 50128 / EN 50129"
    },
    {
        "id": 84,
        "name_en": "Pantograph Carbon Collector Strip",
        "name_zh": "列車集電弓純碳滑板 (Pantograph Strip)",
        "category": "Railway & Transport",
        "beta": 3.0,
        "eta": 15000,
        "mttf_hours": 13400,
        "mttf_years": 2,
        "failure_mode": "電弧侵蝕溝槽、與接觸網硬點撞擊崩塊斷裂 (Chipping)",
        "maintenance_strategy": "每週車底入庫高清晰度影像檢測殘餘厚度 (<5mm更換)",
        "standards": "EN 50408 / IEC 62486"
    },
    {
        "id": 85,
        "name_en": "Train Traction Inverter IGBT Module",
        "name_zh": "列車牽引逆變器 IGBT 功率模組 (VVVF IGBT)",
        "category": "Railway & Transport",
        "beta": 2.1,
        "eta": 100000,
        "mttf_hours": 88500,
        "mttf_years": 12,
        "failure_mode": "熱循環應力引起鍵合線脫落 (Bond-wire lift-off)、底板焊層空洞熱阻上升",
        "maintenance_strategy": "車輛大修週期 (C4/C5) 進行熱阻紅外掃描與門極波形檢測",
        "standards": "IEC 61287-1 / EN 50126"
    },
    {
        "id": 86,
        "name_en": "Rolling Stock Axle Box Tapered Roller Bearing",
        "name_zh": "列車轉向架車軸滾子軸承 (Axle Bearing)",
        "category": "Railway & Transport",
        "beta": 2.7,
        "eta": 130000,
        "mttf_hours": 115700,
        "mttf_years": 15,
        "failure_mode": "接觸疲勞剝落 (Spalling)、軌道雜散電流引起電蝕麻點 (Fluting)",
        "maintenance_strategy": "車載溫度實時遙測監控、定期車下超聲波探傷、軌道側熱軸檢測器 (THDS)",
        "standards": "EN 12080 / ISO 281"
    },
    {
        "id": 87,
        "name_en": "Train Oil-Free Air Brake Compressor",
        "name_zh": "列車無油風冷活塞式空氣制動壓縮機",
        "category": "Railway & Transport",
        "beta": 2.2,
        "eta": 45000,
        "mttf_hours": 39800,
        "mttf_years": 6,
        "failure_mode": "活塞環聚四氟乙烯耐磨層耗盡、吸排氣簧片閥疲勞破裂",
        "maintenance_strategy": "每20000小時更換活塞環組及氣閥套件",
        "standards": "EN 286 / UIC 541-05"
    },
    {
        "id": 88,
        "name_en": "Railway Passenger Saloon Electric Door Actuator",
        "name_zh": "列車客室電動塞拉門機構及電機 (Saloon Door)",
        "category": "Railway & Transport",
        "beta": 2.5,
        "eta": 50000,
        "mttf_hours": 44300,
        "mttf_years": 7,
        "failure_mode": "門控器(EDCU)編碼器故障、主絲桿滾珠磨損、防夾阻力探測漂移",
        "maintenance_strategy": "每月檢查防夾靈敏度、清潔滑道導柱、重新標定關閉力",
        "standards": "EN 14752 / MTR Fleet Maintenance"
    },
    {
        "id": 89,
        "name_en": "Overhead Line (OHL) Composite Polymer Insulator",
        "name_zh": "架空接觸網複合絕緣子 (25kV AC / 1500V DC)",
        "category": "Railway & Transport",
        "beta": 2.3,
        "eta": 200000,
        "mttf_hours": 177000,
        "mttf_years": 25,
        "failure_mode": "沿海高鹽霧潮濕環境引發表面漏電起痕 (Tracking)、芯棒應力腐蝕斷裂",
        "maintenance_strategy": "每年接觸網停電登頂清洗、紫外放電巡檢 (Corona Camera)",
        "standards": "IEC 61109 / IEC 60815"
    },
    {
        "id": 90,
        "name_en": "Railway High-Reliability Signal Light LED Cluster",
        "name_zh": "鐵路高可靠度多顆粒LED信號燈",
        "category": "Railway & Transport",
        "beta": 1.7,
        "eta": 100000,
        "mttf_hours": 89000,
        "mttf_years": 12,
        "failure_mode": "部分LED燈珠開路或短路、恒流驅動電源模組擊穿",
        "maintenance_strategy": "季度巡檢發光強度、信號繼電器電流聯鎖保護檢測",
        "standards": "EN 12368 / MTR Standards"
    },
    {
        "id": 91,
        "name_en": "Industrial Programmable Logic Controller (PLC) CPU",
        "name_zh": "工業可編程控制器 CPU 模組 (Panasonic / Siemens PLC)",
        "category": "Control & Automation",
        "beta": 1.4,
        "eta": 150000,
        "mttf_hours": 136000,
        "mttf_years": 18,
        "failure_mode": "背板通訊匯流排晶片故障、內部固態電容失效、存儲晶片校驗和錯誤 (EEPROM CRC error)",
        "maintenance_strategy": "每年備份程式代碼、更換RTC時鐘鈕扣電池、散熱槽除塵",
        "standards": "IEC 61131-2 / IEC 61508 (SIL2/SIL3)"
    },
    {
        "id": 92,
        "name_en": "PLC Analog Input Module (4-20mA / RTD)",
        "name_zh": "PLC 模擬量輸入模組 (4-20mA A/D Module)",
        "category": "Control & Automation",
        "beta": 1.5,
        "eta": 130000,
        "mttf_hours": 117000,
        "mttf_years": 16,
        "failure_mode": "高精度A/D轉換晶片漂移、光電隔離光耦 (Optocoupler) 光衰老化",
        "maintenance_strategy": "每年用標準信號源校準0-100%量程、零點漂移補償",
        "standards": "IEC 61131-2"
    },
    {
        "id": 93,
        "name_en": "Building Management System (BMS) DDC Controller",
        "name_zh": "樓宇自控直接數字控制器 (BMS DDC Controller)",
        "category": "Control & Automation",
        "beta": 1.6,
        "eta": 120000,
        "mttf_hours": 107000,
        "mttf_years": 15,
        "failure_mode": "BACnet/Modbus 通訊晶片受靜電雷擊擊穿、板載繼電器觸點燒熔",
        "maintenance_strategy": "定期固件補丁更新、檢查總線偏置電阻及浪湧接地",
        "standards": "ASHRAE 135 (BACnet) / EMSD BEC"
    },
    {
        "id": 94,
        "name_en": "Piezoresistive Pressure Transmitter (Water/Steam)",
        "name_zh": "擴散硅壓力變送器 (4-20mA HART)",
        "category": "Control & Automation",
        "beta": 1.6,
        "eta": 100000,
        "mttf_hours": 89500,
        "mttf_years": 12,
        "failure_mode": "不銹鋼隔離膜片被介質雜質穿孔磨損、零點溫漂超差",
        "maintenance_strategy": "每年採用手操泵加壓標定5點校正 (HART Communicator)",
        "standards": "IEC 60770 / ANSI/ISA-51.1"
    },
    {
        "id": 95,
        "name_en": "Pt100 RTD Temperature Sensor with Thermowell",
        "name_zh": "Pt100 鉑熱電阻溫度傳感器及護套",
        "category": "Control & Automation",
        "beta": 1.3,
        "eta": 140000,
        "mttf_hours": 128000,
        "mttf_years": 16,
        "failure_mode": "保護套管(Thermowell)沖刷減薄、接線盒內受潮端子氧化增加阻抗",
        "maintenance_strategy": "每兩年恆溫乾井爐(Dry-well Calibrator)三點對標比對",
        "standards": "IEC 60751 Class A / BS EN 60751"
    },
    {
        "id": 96,
        "name_en": "Pneumatic Control Valve Positioner",
        "name_zh": "智能氣動控制閥門定位器 (Smart Positioner)",
        "category": "Control & Automation",
        "beta": 1.8,
        "eta": 75000,
        "mttf_hours": 66700,
        "mttf_years": 10,
        "failure_mode": "氣源微粒水分堵塞噴嘴擋板/壓電閥、反饋電位器連桿鬆脫",
        "maintenance_strategy": "每月檢查前置空氣過濾減壓閥排污、季度自動調諧行程",
        "standards": "IEC 60534-6 / ISA-75.13"
    },
    {
        "id": 97,
        "name_en": "SCADA Industrial Remote Terminal Unit (RTU)",
        "name_zh": "遠程測控終端單元 (SCADA RTU)",
        "category": "Control & Automation",
        "beta": 1.4,
        "eta": 130000,
        "mttf_hours": 118000,
        "mttf_years": 15,
        "failure_mode": "4G/5G/光纖通訊模組熱死重啟、電源防雷模組擊穿",
        "maintenance_strategy": "定期網絡看門狗(Watchdog)心跳測試、遠程日誌診斷",
        "standards": "IEC 60870-5-104 / IEEE 1613"
    },
    {
        "id": 98,
        "name_en": "Industrial Managed Ethernet Switch",
        "name_zh": "工業級網管型以太網交換機 (Industrial Switch)",
        "category": "Control & Automation",
        "beta": 1.5,
        "eta": 120000,
        "mttf_hours": 108000,
        "mttf_years": 15,
        "failure_mode": "SFP光模塊光功率衰減、電源冗餘雙路輸入故障",
        "maintenance_strategy": "定期查看SNMP告警、環網冗餘協議(RSTP/ERPS)快速收斂測試",
        "standards": "IEEE 802.3 / IEC 61850-3"
    },
    {
        "id": 99,
        "name_en": "DIN-Rail 24VDC Regulated Switching Power Supply",
        "name_zh": "導軌式 24伏直流開關電源 (24VDC PSU)",
        "category": "Control & Automation",
        "beta": 2.2,
        "eta": 80000,
        "mttf_hours": 70800,
        "mttf_years": 10,
        "failure_mode": "輸出端初級高壓濾波電解電容鼓包失容、散熱不良過溫保護鎖死",
        "maintenance_strategy": "每季負載量測紋波電壓 (<50mV)、量度工作溫度",
        "standards": "UL 508 / IEC 61010-1"
    },
    {
        "id": 100,
        "name_en": "Rotary Absolute Encoder (Optical/Magnetic)",
        "name_zh": "絕對值旋轉編碼器 (Absolute Encoder)",
        "category": "Control & Automation",
        "beta": 1.7,
        "eta": 85000,
        "mttf_hours": 75600,
        "mttf_years": 12,
        "failure_mode": "光學碼盤受強烈震動碎裂、旋轉軸油封失效侵入切削液/粉塵",
        "maintenance_strategy": "定期檢查彈性聯軸器同心度與偏角、信號脈衝幅值監測",
        "standards": "IEC 60034 / ISO 12100"
    }
]


@st.cache_data
def get_data():
    return pd.DataFrame(COMPONENTS_RAW)


df = get_data()

# 側邊欄設計
st.sidebar.title("🛠️ 可靠度工程導航")
st.sidebar.caption("香港機電/土木/鐵路/工控設備可靠度數據庫 & DIF 預測平台")

menu = st.sidebar.radio(
    "選擇功能模組 / Function Modules:",
    [
        "🔍 100 款工程組件庫 (Component Database)",
        "📈 韋伯可靠度分析 (Weibull & Failure Rate)",
        "⏳ 剩餘壽命預測 (RUL & Conditional Reliability)",
        "🔬 領域不變特徵 (Domain Invariant Features - DIF)",
        "🔄 系統冗餘可靠度計算 (System Redundancy Calculator)"
    ]
)

st.sidebar.markdown("---")
st.sidebar.info("""
**📚 參考文獻與法規標準：**
- **IEEE Std 493 (Gold Book)**: 工商業電力系統可靠度設計
- **OREDA (Offshore & Onshore Reliability Data)**
- **EMSD CoP**: 機電工程署各項設備實務守則
- **FSD CoP & Circular Letters**: 消防處系統守則
- **MTR Engineering Standards**: 鐵路信號與車輛維修指引
- **CIBSE Guide M**: 屋宇裝備維護與壽命周期管理
""")

# -------------------------------------------------------------
# 模組 1: 100 款工程組件數據庫
# -------------------------------------------------------------
if menu == "🔍 100 款工程組件庫 (Component Database)":
    st.header("🔍 香港工程常見 100 款組件可靠度數據庫")
    st.markdown("""
    本資料庫涵蓋香港 7 大關鍵工程範疇共 **100 種核心設備與組件**，提供標準 **Weibull 形狀參數 ($\\beta$)**、**尺度參數 ($\\eta$)**、**MTTF**、**典型失效模式** 及 **香港法定檢驗/保養指引**。
    """)

    col1, col2 = st.columns([1, 2])
    with col1:
        cat_list = ["全部範疇 (All Categories)"] + sorted(list(df['category'].unique()))
        selected_cat = st.selectbox("工程專業領域分類：", cat_list)
    with col2:
        search = st.text_input("關鍵字搜尋（支援中文、英文或失效機理，如 Chiller, 變壓器, 泵, 斷路器, 軸承）:", "")

    filtered_df = df.copy()
    if selected_cat != "全部範疇 (All Categories)":
        filtered_df = filtered_df[filtered_df['category'] == selected_cat]
    if search:
        filtered_df = filtered_df[
            filtered_df['name_en'].str.contains(search, case=False, na=False) |
            filtered_df['name_zh'].str.contains(search, case=False, na=False) |
            filtered_df['failure_mode'].str.contains(search, case=False, na=False) |
            filtered_df['standards'].str.contains(search, case=False, na=False)
            ]

    st.markdown(f"**共篩選出 `{len(filtered_df)}` 項工程組件**")

    # 顯示精簡表格
    display_df = filtered_df[
        ['id', 'name_zh', 'name_en', 'category', 'beta', 'eta', 'mttf_hours', 'mttf_years', 'failure_mode',
         'standards']].copy()
    display_df.columns = ['ID', '中文名稱 (行內稱呼)', 'English Name', '範疇', 'Weibull β', 'Weibull η (小時)',
                          'MTTF (小時)', '設計壽命 (年)', '主要失效模式', '適用標準規範']
    st.dataframe(display_df, use_container_width=True, hide_index=True)

    # 詳細展開卡片
    st.subheader("📋 組件詳細工程可靠度卡片")
    selected_comp_id = st.selectbox(
        "選擇組件查看詳細工程維修資訊：",
        filtered_df['id'].tolist(),
        format_func=lambda
            x: f"#{x} - {df.loc[df['id'] == x, 'name_zh'].values[0]} ({df.loc[df['id'] == x, 'name_en'].values[0]})"
    )

    if selected_comp_id:
        c_info = df[df['id'] == selected_comp_id].iloc[0]
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Weibull 形狀參數 (β)", f"{c_info['beta']:.2f}")
        c2.metric("Weibull 尺度參數 (η)", f"{c_info['eta']:,} hrs")
        c3.metric("平均無故障時間 (MTTF)", f"{c_info['mttf_hours']:,} hrs")
        c4.metric("等效設計壽命", f"約 {c_info['mttf_years']} 年")

        st.markdown(f"""
        - **設備名稱**：`{c_info['name_zh']}` | `{c_info['name_en']}`
        - **所屬工程範疇**：`{c_info['category']}`
        - **主要物理失效模式**：{c_info['failure_mode']}
        - **香港工程實務保養策略**：{c_info['maintenance_strategy']}
        - **遵從法例標準與參考規範**：`{c_info['standards']}`
        """)

# -------------------------------------------------------------
# 模組 2: 韋伯 (Weibull) 可靠度與失效率浴盆曲線
# -------------------------------------------------------------
elif menu == "📈 韋伯可靠度分析 (Weibull & Failure Rate)":
    st.header("📈 韋伯分布 (Weibull Distribution) 可靠度與失效率分析")
    st.markdown("""
    韋伯分布係可靠度工程中最廣泛應用嘅數學模型。
    - **可靠度函數 (Reliability)**：$R(t) = \exp\left( -\left(\frac{t}{\eta}\right)^\beta \right)$
    - **累積失效機率 (CDF)**：$F(t) = 1 - R(t)$
    - **失效率 / 危害率 (Hazard Rate)**：$h(t) = \frac{\beta}{\eta} \left(\frac{t}{\eta}\right)^{\beta - 1}$
    """)

    col_ctrl1, col_ctrl2 = st.columns([2, 1])
    with col_ctrl1:
        comp_choice = st.selectbox(
            "從資料庫選取組件自動載入參數：",
            df['id'].tolist(),
            format_func=lambda
                x: f"#{x} - {df.loc[df['id'] == x, 'name_zh'].values[0]} ({df.loc[df['id'] == x, 'name_en'].values[0]})"
        )
        comp_row = df[df['id'] == comp_choice].iloc[0]

    with col_ctrl2:
        custom_param = st.checkbox("自定義手動調節參數 (Manual Override)", False)

    if custom_param:
        c1, c2 = st.columns(2)
        beta_val = c1.number_input("形狀參數 β (Shape Parameter):", min_value=0.1, max_value=10.0,
                                   value=float(comp_row['beta']), step=0.1)
        eta_val = c2.number_input("尺度參數 η (Scale Parameter, hrs):", min_value=100, max_value=1000000,
                                  value=int(comp_row['eta']), step=1000)
    else:
        beta_val = float(comp_row['beta'])
        eta_val = float(comp_row['eta'])

    # 浴盆曲線階段解讀
    st.subheader("💡 形狀參數 $\\beta$ 物理工程意涵：")
    if beta_val < 1.0:
        st.warning(
            f"當前 **β = {beta_val} < 1**：屬於 **早期失效期 (Infant Mortality)**。組件失效率隨時間遞減，通常由出廠瑕疵、裝配不良或試運轉磨合問題引起。對策：出廠前高低溫老化篩選 (Burn-in) 及現場嚴格驗收。")
    elif abs(beta_val - 1.0) < 0.05:
        st.info(
            f"當前 **β = {beta_val} ≈ 1**：屬於 **偶然失效期 (Constant Failure Rate / Exponential)**。失效率恆定為 $h(t) = 1/\eta$，失效純粹由外部環境隨機衝擊引起。預防性更換無助降低失效率。")
    else:
        st.success(
            f"當前 **β = {beta_val} > 1**：屬於 **耗損磨損期 (Wear-out Phase)**。失效率隨運轉時間加速上升，反映金屬疲勞、軸承磨損、絕緣熱老化等機理。此階段實施定期預防性維護 (CBM/PdM) 效益最高！")

    # 計算並繪製曲線
    max_t = int(eta_val * 2.0)
    t = np.linspace(0, max_t, 500)
    # 避免 t=0 時當 beta<1 產生除以零警告
    t_safe = np.where(t == 0, 1e-6, t)

    R_t = np.exp(- (t_safe / eta_val) ** beta_val)
    F_t = 1.0 - R_t
    h_t = (beta_val / eta_val) * ((t_safe / eta_val) ** (beta_val - 1.0))

    fig, axes = plt.subplots(1, 3, figsize=(18, 5))

    # 圖 1: R(t)
    axes[0].plot(t, R_t, color='royalblue', lw=2.5)
    axes[0].axvline(eta_val, color='darkorange', linestyle='--', label=f'Characteristic Life η ({eta_val:,}h)')
    axes[0].axhline(np.exp(-1), color='gray', linestyle=':', label='R(η) = 36.8%')
    axes[0].set_title("Reliability Function R(t)", fontsize=13)
    axes[0].set_xlabel("Operating Time t (hours)")
    axes[0].set_ylabel("Reliability R(t)")
    axes[0].set_ylim([-0.05, 1.05])
    axes[0].grid(True, alpha=0.3)
    axes[0].legend()

    # 圖 2: F(t)
    axes[1].plot(t, F_t, color='crimson', lw=2.5)
    axes[1].axvline(eta_val, color='darkorange', linestyle='--', label=f'Characteristic Life η')
    axes[1].axhline(1.0 - np.exp(-1), color='gray', linestyle=':', label='F(η) = 63.2%')
    axes[1].set_title("Cumulative Failure Probability F(t)", fontsize=13)
    axes[1].set_xlabel("Operating Time t (hours)")
    axes[1].set_ylabel("Failure Probability F(t)")
    axes[1].set_ylim([-0.05, 1.05])
    axes[1].grid(True, alpha=0.3)
    axes[1].legend()

    # 圖 3: h(t)
    axes[2].plot(t[1:], h_t[1:] * 1e6, color='forestgreen', lw=2.5)
    axes[2].set_title("Hazard Rate h(t) (Failures per 10^6 hrs / FIT)", fontsize=13)
    axes[2].set_xlabel("Operating Time t (hours)")
    axes[2].set_ylabel("Hazard Rate h(t) [x 10^-6]")
    axes[2].grid(True, alpha=0.3)

    st.pyplot(fig)

    # 交互式即時計算
    st.markdown("---")
    st.subheader("🔢 即時運轉時數可靠度查詢")
    query_t = st.number_input("輸入組件已運轉時數 (小時):", min_value=0, max_value=max_t, value=int(eta_val * 0.5),
                              step=1000)
    q_t_safe = max(query_t, 1e-6)
    q_R = float(np.exp(- (q_t_safe / eta_val) ** beta_val))
    q_F = 1.0 - q_R
    q_h = float((beta_val / eta_val) * ((q_t_safe / eta_val) ** (beta_val - 1.0)))

    qc1, qc2, qc3 = st.columns(3)
    qc1.metric("目前可靠度 R(t)", f"{q_R * 100:.2f} %")
    qc2.metric("累積失效機率 F(t)", f"{q_F * 100:.2f} %")
    qc3.metric("瞬時失效率 h(t)", f"{q_h * 1e6:.2f} FIT (每百萬小時)")

# -------------------------------------------------------------
# 模組 3: 剩餘壽命 (RUL) 與條件可靠度預測
# -------------------------------------------------------------
elif menu == "⏳ 剩餘壽命預測 (RUL & Conditional Reliability)":
    st.header("⏳ 剩餘有效使用壽命 (RUL) 與條件可靠度預測")
    st.markdown("""
    在香港工務工程與物業維護中，設備通常已運轉數年（$t_0$ 小時）。工程師最需要評估的是：
    **「若設備已正常運轉至 $t_0$ 小時，在未來額外運轉 $\\Delta t$ 小時內不發生故障的機率是多少？」**

    - **條件可靠度公式**：
      $$R(\Delta t \mid t_0) = \frac{R(t_0 + \Delta t)}{R(t_0)} = \exp\left( - \left[ \left(\frac{t_0 + \Delta t}{\eta}\right)^\beta - \left(\frac{t_0}{\eta}\right)^\beta \right] \right)$$
    """)

    col1, col2 = st.columns(2)
    with col1:
        comp_id = st.selectbox(
            "選擇評估組件：",
            df['id'].tolist(),
            format_func=lambda
                x: f"#{x} - {df.loc[df['id'] == x, 'name_zh'].values[0]} ({df.loc[df['id'] == x, 'name_en'].values[0]})"
        )
        c_item = df[df['id'] == comp_id].iloc[0]
        beta = float(c_item['beta'])
        eta = float(c_item['eta'])
        mttf = float(c_item['mttf_hours'])

        st.info(f"**組件：** {c_item['name_zh']} | **β = {beta}**, **η = {eta:,} hrs**, **MTTF = {mttf:,} hrs**")

    with col2:
        current_age = st.number_input("現有已累積運轉時數 $t_0$ (小時):", min_value=0, max_value=int(eta * 2),
                                      value=int(eta * 0.4), step=1000)
        target_reliability = st.slider("目標可靠度安全閾值 $R_{target}$ (%):", min_value=50, max_value=99,
                                       value=90) / 100.0

    # RUL 計算：解 R(t_target) = R_target => t_target = eta * (-ln(R_target))^(1/beta)
    t_target = eta * ((- np.log(target_reliability)) ** (1.0 / beta))
    rul_hours = max(0.0, t_target - current_age)
    rul_years = rul_hours / 8760.0  # 假設年運轉 8760 小時（24/7）或依工況

    st.subheader("📊 RUL 預測結論與建議：")
    r1, r2, r3 = st.columns(3)
    r1.metric("達到目標可靠度的總壽命 $t_{target}$", f"{int(t_target):,} hrs")
    r2.metric("預測剩餘有效壽命 (RUL)", f"{int(rul_hours):,} hrs", delta=f"{rul_years:.1f} 年 (24x7)")
    current_R = np.exp(- (max(current_age, 1e-6) / eta) ** beta)
    r3.metric("當前年齡累積可靠度 $R(t_0)$", f"{current_R * 100:.2f} %")

    # 未來維修週期（例如未來 1 年 = 8760 小時）的條件可靠度
    delta_t_list = [2190, 4380, 8760, 17520]
    st.markdown("#### 📅 未來維修窗口期內之條件可靠度 $R(\Delta t \mid t_0)$：")
    cond_results = []
    for dt in delta_t_list:
        R_future = np.exp(- ((current_age + dt) / eta) ** beta)
        cond_R = R_future / current_R if current_R > 0 else 0
        cond_results.append({
            "未來運轉時間 (Δt)": f"{dt:,} 小時 (約 {dt // 8760 if dt >= 8760 else dt // 720} {'年' if dt >= 8760 else '個月'})",
            "條件可靠度 R(Δt|t0)": f"{cond_R * 100:.2f} %",
            "條件失效風險": f"{(1.0 - cond_R) * 100:.2f} %",
            "建議工程行動": "正常巡檢" if cond_R > 0.9 else (
                "加強震動/熱成像檢測" if cond_R > 0.75 else "立即安排大修或預防性更換")
        })
    st.table(pd.DataFrame(cond_results))

# -------------------------------------------------------------
# 模組 4: 領域不變特徵 (Domain Invariant Features - DIF)
# -------------------------------------------------------------
elif menu == "🔬 領域不變特徵 (Domain Invariant Features - DIF)":
    st.header("🔬 領域不變特徵 (DIF) 在香港動態工況下的應用")
    st.markdown("""
    在香港的高層建築與基建設施中，設備經常面臨**劇烈工況波動**（例如：夏季 34°C 高溫高濕滿載運轉 vs. 冬季低溫低負載）。
    傳統振動或電流特徵會隨負載變化發生**分佈漂移 (Distribution Shift)**，導致將工況波動誤判為設備老化。

    **領域不變特徵 (Domain Invariant Features, DIF)** 核心目標：
    透過對抗學習或最大均值差異 (Maximum Mean Discrepancy, MMD) 約束，**消除工況領域差異，保留單調退化趨勢**，從而實現跨工況的精準 RUL 預測。
    """)

    st.subheader("🧪 交互式模擬：夏季滿載 (Domain A) vs 冬季低載 (Domain B)")

    np.random.seed(42)
    time_steps = np.linspace(0, 100, 200)

    # 真實物理退化趨勢（單調指數增長）
    true_health_degradation = 0.05 * np.exp(0.03 * time_steps)

    # 傳統非不變特徵（例如未補償之原始振動 RMS）：受工況影響劇烈（夏天負載高，振幅基底大）
    domain_A_load = 1.8  # 夏季高溫滿載
    domain_B_load = 0.8  # 冬季低載

    raw_feature_A = true_health_degradation * domain_A_load + np.random.normal(0, 0.04, len(time_steps)) + 0.5
    raw_feature_B = true_health_degradation * domain_B_load + np.random.normal(0, 0.04, len(time_steps)) + 0.1

    # 經過 DIF (Domain Invariant Mapping) 提取後之特徵：消除工況基底與增益偏移
    dif_feature_A = true_health_degradation + np.random.normal(0, 0.02, len(time_steps))
    dif_feature_B = true_health_degradation + np.random.normal(0, 0.02, len(time_steps))

    # 計算 MMD (簡化一階矩差異表示)
    mmd_raw = np.abs(np.mean(raw_feature_A) - np.mean(raw_feature_B))
    mmd_dif = np.abs(np.mean(dif_feature_A) - np.mean(dif_feature_B))

    m1, m2 = st.columns(2)
    m1.metric("原始特徵領域差異 (Raw Feature Divergence)", f"{mmd_raw:.4f}")
    m2.metric("DIF 特徵領域差異 (DIF Divergence - MMD)", f"{mmd_dif:.4f}",
              delta=f"-{(1 - mmd_dif / mmd_raw) * 100:.1f}% 領域漂移降低")

    fig2, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 5))

    # 原始特徵分佈
    ax1.plot(time_steps, raw_feature_A, 'r-', label='Domain A (Summer Peak Load, 100%)', alpha=0.8)
    ax1.plot(time_steps, raw_feature_B, 'b-', label='Domain B (Winter Low Load, 40%)', alpha=0.8)
    ax1.axhline(1.2, color='gray', linestyle='--', label='Fixed Warning Threshold')
    ax1.set_title("❌ Raw Features (Coupled with Operational Noise)", fontsize=12)
    ax1.set_xlabel("Operational Life (%)")
    ax1.set_ylabel("Vibration RMS / Raw Amplitude")
    ax1.grid(True, alpha=0.3)
    ax1.legend()

    # DIF 特徵分佈
    ax2.plot(time_steps, dif_feature_A, 'g-', label='Domain A (DIF Health Index)', alpha=0.8)
    ax2.plot(time_steps, dif_feature_B, 'm--', label='Domain B (DIF Health Index)', alpha=0.8)
    ax2.axhline(0.8, color='crimson', linestyle='--', label='Reliable Failure Threshold')
    ax2.set_title("✅ Domain Invariant Features (DIF - True Degradation)", fontsize=12)
    ax2.set_xlabel("Operational Life (%)")
    ax2.set_ylabel("Domain-Invariant Health Index (HI)")
    ax2.grid(True, alpha=0.3)
    ax2.legend()

    st.pyplot(fig2)

    st.markdown("""
    #### 🎓 工程意義與畢業設計 (FYP) 亮點：
    1. **傳統方法的盲點**：夏季高載時，振動因負載增大而升高，容易誤觸固定告警線（如左圖灰色虛線）；冬季低載時，即便軸承嚴重剝落磨損，振幅仍偏低，可能造成漏報。
    2. **DIF 的優勢**：提取領域不變特徵後，兩條退化曲線高度重合（右圖），使同一套閾值或神經網絡在全年各種工況下均能準確預測剩餘壽命。
    """)

# -------------------------------------------------------------
# 模組 5: 系統冗餘可靠度計算器 (Redundancy Calculator)
# -------------------------------------------------------------
elif menu == "🔄 系統冗餘可靠度計算 (System Redundancy Calculator)":
    st.header("🔄 系統級冗餘可靠度計算器 (System Redundancy Calculator)")
    st.markdown("""
    在香港工程設計中（如醫院、數據中心、鐵路牽引供電），關鍵設備皆採用冗餘設計（例如：水泵「一用一備 (1 Duty 1 Standby)」，冷凍機組「$k$-out-of-$n$」配置）。
    """)

    calc_type = st.radio("選擇系統架構類型：", ["串聯系統 (Series System - 任何一組件失效即停機)",
                                               "並聯熱備份系統 (Parallel Active Redundancy - 1-out-of-n)",
                                               "k-out-of-n 系統 (如 3 部冷水機至少需 2 部運行)"])

    if calc_type == "串聯系統 (Series System - 任何一組件失效即停機)":
        st.write("系統可靠度：$R_{sys}(t) = \prod_{i=1}^n R_i(t)$")
        n_comp = st.slider("串聯組件數量：", 2, 5, 3)
        cols = st.columns(n_comp)
        R_vals = []
        for idx, col in enumerate(cols):
            with col:
                r = st.number_input(f"組件 {idx + 1} 可靠度 R_{idx + 1}:", 0.0, 1.0, 0.95, 0.01)
                R_vals.append(r)
        R_sys = float(np.prod(R_vals))
        st.metric("整體系統可靠度 R_sys", f"{R_sys * 100:.3f} %")

    elif calc_type == "並聯熱備份系統 (Parallel Active Redundancy - 1-out-of-n)":
        st.write("系統可靠度：$R_{sys}(t) = 1 - \prod_{i=1}^n (1 - R_i(t))$")
        n_comp = st.slider("並聯設備數量 (如一用一備 n=2, 一用兩備 n=3)：", 2, 4, 2)
        cols = st.columns(n_comp)
        R_vals = []
        for idx, col in enumerate(cols):
            with col:
                r = st.number_input(f"設備 {idx + 1} 可靠度 R_{idx + 1}:", 0.0, 1.0, 0.90, 0.01)
                R_vals.append(r)
        F_sys = float(np.prod([1.0 - r for r in R_vals]))
        R_sys = 1.0 - F_sys
        st.metric("冗餘備份後系統可靠度 R_sys", f"{R_sys * 100:.4f} %",
                  delta=f"+{(R_sys - min(R_vals)) * 100:.2f}% 可靠度提升")

    elif calc_type == "k-out-of-n 系統 (如 3 部冷水機至少需 2 部運行)":
        st.write("假設所有單元可靠度均為 $R$，則系統可靠度：$R_{k/n} = \sum_{i=k}^n \binom{n}{i} R^i (1-R)^{n-i}$")
        c1, c2, c3 = st.columns(3)
        n = c1.number_input("總機組數量 n:", 2, 10, 3)
        k = c2.number_input("維持運作所需最低數量 k:", 1, n, 2)
        r_unit = c3.number_input("單一機組可靠度 R:", 0.0, 1.0, 0.90, 0.01)

        from scipy.special import comb

        r_kn = sum(comb(n, i) * (r_unit ** i) * ((1.0 - r_unit) ** (n - i)) for i in range(k, n + 1))
        st.metric(f"{k}-out-of-{n} 系統可靠度", f"{r_kn * 100:.4f} %")

st.markdown("---")
st.caption("Developed for Hong Kong Engineering Community & Academic Research | Powered by Python, Streamlit & Scipy")

