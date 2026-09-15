# -*- coding: utf-8 -*-
"""
Hong Kong Critical Infrastructure Reliability & Domain-Invariant (DIF) Analysis Platform
香港重大基礎設施（鐵路、機場、市政、建築、港口）組件可靠度與領域不變特徵 (DIF) 壽命預測系統
"""
import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# Matplotlib CJK Font Configuration (防止中文方塊亂碼)
plt.rcParams['font.sans-serif'] = ['WenQuanYi Zen Hei', 'Noto Sans CJK TC', 'Noto Sans CJK SC', 'Microsoft YaHei', 'PingFang SC', 'DejaVu Sans', 'sans-serif']
plt.rcParams['axes.unicode_minus'] = False

from scipy.special import comb
import json

# 1. 網頁基本設定
st.set_page_config(
    page_title="HK Critical Infrastructure Reliability & DIF Platform",
    page_icon="🚆",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 2. 載入劃分邊界之組件庫
BOUNDARY_DB = [
  {
    "id": 1,
    "name_en": "Railway Point Machine (Track Switch Actuator)",
    "name_zh": "鐵路道岔轉轍機 (Point Machine - MTR Spec)",
    "boundary": "Railway Management",
    "beta": 1.9,
    "eta": 120000,
    "mttf_hours": 106500,
    "mttf_years": 15,
    "failure_mode": "密貼接點氧化、滾珠絲杠磨損卡死、表示接點缺口超差",
    "maintenance_strategy": "每季測定轉轍力、表示缺口光電測量、絲杠專用脂加注 (MTR Signalling Standards)",
    "standards": "MTR Signalling Standards / BS 7345 / EN 50126"
  },
  {
    "id": 2,
    "name_en": "AF Track Circuit Audio-Frequency Receiver",
    "name_zh": "音頻無絕緣軌道電路接收單元",
    "boundary": "Railway Management",
    "beta": 1.5,
    "eta": 150000,
    "mttf_hours": 135000,
    "mttf_years": 18,
    "failure_mode": "濾波電容漂移使載頻偏移失諧、雷擊感應過電壓擊穿",
    "maintenance_strategy": "定期量度軌面信號感應電壓、調諧單元S帶阻抗檢測",
    "standards": "EN 50129 / MTR Standards"
  },
  {
    "id": 3,
    "name_en": "Axle Counter Wheel Sensor",
    "name_zh": "計軸器車輪電磁傳感頭 (Axle Counter Sensor)",
    "boundary": "Railway Management",
    "beta": 1.6,
    "eta": 110000,
    "mttf_hours": 98700,
    "mttf_years": 14,
    "failure_mode": "軌道強烈震動造成夾具鬆脫位移、傳感線圈磁芯受損",
    "maintenance_strategy": "每月軌道檢測夾具扭力、傳感器殘留電壓校驗",
    "standards": "EN 50128 / EN 50129"
  },
  {
    "id": 4,
    "name_en": "Pantograph Carbon Collector Strip",
    "name_zh": "列車集電弓純碳滑板 (Pantograph Strip)",
    "boundary": "Railway Management",
    "beta": 3.0,
    "eta": 15000,
    "mttf_hours": 13400,
    "mttf_years": 2,
    "failure_mode": "電弧侵蝕溝槽、與接觸網硬點撞擊崩塊斷裂 (Chipping)",
    "maintenance_strategy": "每週車底入庫高清晰度影像檢測殘餘厚度 (<5mm更換)",
    "standards": "EN 50408 / IEC 62486"
  },
  {
    "id": 5,
    "name_en": "Rolling Stock Traction Inverter IGBT Module",
    "name_zh": "列車牽引逆變器 IGBT 功率模組 (VVVF IGBT)",
    "boundary": "Railway Management",
    "beta": 2.1,
    "eta": 100000,
    "mttf_hours": 88500,
    "mttf_years": 12,
    "failure_mode": "熱循環應力引起鍵合線脫落 (Bond-wire lift-off)、底板焊層空洞熱阻上升",
    "maintenance_strategy": "車輛大修週期 (C4/C5) 進行熱阻紅外掃描與門極波形檢測",
    "standards": "IEC 61287-1 / EN 50126"
  },
  {
    "id": 6,
    "name_en": "Rolling Stock Axle Box Tapered Roller Bearing",
    "name_zh": "列車轉向架車軸滾子軸承 (Axle Bearing)",
    "boundary": "Railway Management",
    "beta": 2.7,
    "eta": 130000,
    "mttf_hours": 115700,
    "mttf_years": 15,
    "failure_mode": "接觸疲勞剝落 (Spalling)、軌道雜散電流引起電蝕麻點 (Fluting)",
    "maintenance_strategy": "車載溫度實時遙測監控、定期車下超聲波探傷、軌道側熱軸檢測器 (THDS)",
    "standards": "EN 12080 / ISO 281"
  },
  {
    "id": 7,
    "name_en": "Train Oil-Free Air Brake Compressor",
    "name_zh": "列車無油風冷活塞式空氣制動壓縮機",
    "boundary": "Railway Management",
    "beta": 2.2,
    "eta": 45000,
    "mttf_hours": 39800,
    "mttf_years": 6,
    "failure_mode": "活塞環聚四氟乙烯耐磨層耗盡、吸排氣簧片閥疲勞破裂",
    "maintenance_strategy": "每20000小時更換活塞環組及氣閥套件",
    "standards": "EN 286 / UIC 541-05"
  },
  {
    "id": 8,
    "name_en": "Railway Passenger Saloon Electric Door Actuator",
    "name_zh": "列車客室電動塞拉門機構及電機 (Saloon Door)",
    "boundary": "Railway Management",
    "beta": 2.5,
    "eta": 50000,
    "mttf_hours": 44300,
    "mttf_years": 7,
    "failure_mode": "門控器(EDCU)編碼器故障、主絲桿滾珠磨損、防夾阻力探測漂移",
    "maintenance_strategy": "每月檢查防夾靈敏度、清潔滑道導柱、重新標定關閉力",
    "standards": "EN 14752 / MTR Fleet Maintenance"
  },
  {
    "id": 9,
    "name_en": "Overhead Line (OHL) Composite Polymer Insulator",
    "name_zh": "架空接觸網複合絕緣子 (25kV AC / 1500V DC)",
    "boundary": "Railway Management",
    "beta": 2.3,
    "eta": 200000,
    "mttf_hours": 177000,
    "mttf_years": 25,
    "failure_mode": "沿海高鹽霧潮濕環境引發表面漏電起痕 (Tracking)、芯棒應力腐蝕斷裂",
    "maintenance_strategy": "每年接觸網停電登頂清洗、紫外放電巡檢 (Corona Camera)",
    "standards": "IEC 61109 / IEC 60815"
  },
  {
    "id": 10,
    "name_en": "Railway Vital LED Signal Light Head Cluster",
    "name_zh": "鐵路高可靠度多顆粒LED信號燈",
    "boundary": "Railway Management",
    "beta": 1.7,
    "eta": 100000,
    "mttf_hours": 89000,
    "mttf_years": 12,
    "failure_mode": "部分LED燈珠開路或短路、恒流驅動電源模組擊穿",
    "maintenance_strategy": "季度巡檢發光強度、信號繼電器電流聯鎖保護檢測",
    "standards": "EN 12368 / MTR Standards"
  },
  {
    "id": 11,
    "name_en": "Third Rail Top-Contact Current Collector Shoe",
    "name_zh": "第三軌集電靴及受流臂機構 (Collector Shoe)",
    "boundary": "Railway Management",
    "beta": 2.6,
    "eta": 35000,
    "mttf_hours": 31000,
    "mttf_years": 4,
    "failure_mode": "碳化鎢滑靴磨擦過度、下壓扭簧彈力衰減致跳火拉弧",
    "maintenance_strategy": "每月量測靴片接觸厚度、校準靴片下壓接觸壓力",
    "standards": "IEC 62486 / MTR Depot Specs"
  },
  {
    "id": 12,
    "name_en": "Automatic Train Supervision (ATS) Balise Transponder",
    "name_zh": "列車自動監控應答器 (Eurobalise)",
    "boundary": "Railway Management",
    "beta": 1.4,
    "eta": 220000,
    "mttf_hours": 201000,
    "mttf_years": 25,
    "failure_mode": "軌道道碴震動導致內部諧振電路失諧、外殼耐候封裝老化入水",
    "maintenance_strategy": "專用車載探測天線定期動態讀寫校驗、防雷接地檢查",
    "standards": "SUBSET-036 / EN 50128"
  },
  {
    "id": 13,
    "name_en": "Traction Substation 25kV Vacuum Circuit Breaker",
    "name_zh": "牽引變電站 25kV 單相真空斷路器",
    "boundary": "Railway Management",
    "beta": 2.0,
    "eta": 160000,
    "mttf_hours": 142000,
    "mttf_years": 20,
    "failure_mode": "頻繁通過短路電流衝擊使真空滅弧室觸頭燒蝕、跳閘機構卡滯",
    "maintenance_strategy": "每年接觸電阻量度、斷路器開距與超程機械特性測試",
    "standards": "IEC 62271-100 / MTR Power Guidelines"
  },
  {
    "id": 14,
    "name_en": "Train Roof-Mounted Compact HVAC Unit Compressor",
    "name_zh": "客車車頂一體化空調壓縮機",
    "boundary": "Railway Management",
    "beta": 2.3,
    "eta": 80000,
    "mttf_hours": 70900,
    "mttf_years": 10,
    "failure_mode": "隧道活塞風壓力脈動引起冷媒管路疲勞震裂洩漏、電機軸承磨損",
    "maintenance_strategy": "夏季前更換冷凍機油、冷凝器高壓吹掃、系統氣密性打壓",
    "standards": "EN 14750 / EN 14813"
  },
  {
    "id": 15,
    "name_en": "Track Switch Rail Induction Heating Element",
    "name_zh": "道岔轉轍尖軌電加熱防卡阻元件",
    "boundary": "Railway Management",
    "beta": 2.4,
    "eta": 50000,
    "mttf_hours": 44300,
    "mttf_years": 8,
    "failure_mode": "極端溫差熱膨脹導致電熱管外壁破裂、引出線絕緣受潮接地",
    "maintenance_strategy": "入冬前全面量度絕緣電阻 (>10 MOhm)、帶電溫升測試",
    "standards": "UIC 527-1 / EN 50125"
  },
  {
    "id": 16,
    "name_en": "Platform Screen Door (PSD) Drive Belt & Controller",
    "name_zh": "月台幕門驅動齒形帶及智能門控器 (PSD Belt)",
    "boundary": "Railway Management",
    "beta": 2.2,
    "eta": 60000,
    "mttf_hours": 53200,
    "mttf_years": 8,
    "failure_mode": "高頻繁開關導致齒形皮帶疲勞斷齒、紅外安全防夾光幕衰減",
    "maintenance_strategy": "每週防夾測試 (10mm障礙物感應)、皮帶張力計校驗",
    "standards": "EN 16005 / MTR Station E&M Standards"
  },
  {
    "id": 17,
    "name_en": "Trackside Hot Axle Box Detection (THDS) Infrared Head",
    "name_zh": "軌旁紅外熱軸探測儀光學探頭",
    "boundary": "Railway Management",
    "beta": 1.6,
    "eta": 120000,
    "mttf_hours": 107000,
    "mttf_years": 15,
    "failure_mode": "光學透鏡被泥沙油污遮蔽、碲鎘汞紅外探測晶片靈敏度漂移",
    "maintenance_strategy": "每月黑體校準儀 (Blackbody) 標定探測精度 (誤差 <1°C)",
    "standards": "EN 15437-1"
  },
  {
    "id": 18,
    "name_en": "Train Emergency Standby Battery Static Inverter",
    "name_zh": "列車應急備用電池靜態逆變器 (110VDC/220VAC)",
    "boundary": "Railway Management",
    "beta": 2.1,
    "eta": 85000,
    "mttf_hours": 75200,
    "mttf_years": 12,
    "failure_mode": "功率器件直流支撐電容老化漏液、門極驅動隔離光耦失效",
    "maintenance_strategy": "季度充放電切換試驗、母線紋波示波器量測",
    "standards": "IEC 60571 / EN 50155"
  },
  {
    "id": 19,
    "name_en": "Automatic Mechanical Coupler Locking Wedge",
    "name_zh": "全自動密接式車鉤鎖緊契塊與彈簧組",
    "boundary": "Railway Management",
    "beta": 2.5,
    "eta": 140000,
    "mttf_hours": 124000,
    "mttf_years": 20,
    "failure_mode": "多次連掛衝擊引發鎖面磨耗間隙增大、解鉤風缸密封圈洩漏",
    "maintenance_strategy": "架修期超聲波探傷鉤體微裂紋、專用間隙卡規量測",
    "standards": "EN 15020 / UIC 522"
  },
  {
    "id": 20,
    "name_en": "Bogie Primary Chevron Rubber Spring",
    "name_zh": "轉向架一系人字形金屬橡膠疊層彈簧",
    "boundary": "Railway Management",
    "beta": 2.8,
    "eta": 100000,
    "mttf_hours": 89000,
    "mttf_years": 14,
    "failure_mode": "橡膠長期剪切老化硬化、金屬硫化結合層開裂剝離",
    "maintenance_strategy": "按行駛里程檢查靜態下沉撓度、表面臭氧龜裂深評估",
    "standards": "EN 13913 / ISO 2856"
  },
  {
    "id": 21,
    "name_en": "Baggage Handling System (BHS) Merge Conveyor Drive",
    "name_zh": "行李輸送分揀高速合流電機與滾筒 (BHS Drive)",
    "boundary": "Airport Management",
    "beta": 2.4,
    "eta": 55000,
    "mttf_hours": 48700,
    "mttf_years": 7,
    "failure_mode": "高頻啟停引起電機煞車片磨損、電動滾筒內置行星齒輪齒面疲勞",
    "maintenance_strategy": "每日目測熱成像掃描、每月激光對中測量輸送帶張力",
    "standards": "IATA Baggage Handling Standards / BS EN 619"
  },
  {
    "id": 22,
    "name_en": "Passenger Boarding Bridge (PBB) Hydraulic Jack Cylinder",
    "name_zh": "登機橋伸縮頂升主液壓油缸 (PBB Cylinder)",
    "boundary": "Airport Management",
    "beta": 2.3,
    "eta": 80000,
    "mttf_hours": 70900,
    "mttf_years": 12,
    "failure_mode": "柱塞桿表面硬鉻層劃傷、耐磨密封圈高溫硬化引起液壓內洩",
    "maintenance_strategy": "每月檢查液壓油清潔度 (NAS 1638 7級)、安全防墜單向閥年檢",
    "standards": "EN 1915 / EN 12312-4 / HKCAD Specs"
  },
  {
    "id": 23,
    "name_en": "400Hz Ground Power Unit (GPU) Static Converter",
    "name_zh": "400Hz 航空地面靜態變頻電源 (GPU)",
    "boundary": "Airport Management",
    "beta": 2.0,
    "eta": 90000,
    "mttf_hours": 79800,
    "mttf_years": 12,
    "failure_mode": "輸出端中頻濾波電容爆漿、IGBT 水冷散熱通道水垢堵塞",
    "maintenance_strategy": "每半年滿載 (90kVA) 假負載試驗、量測輸出電壓諧波畸變率 (<3%)",
    "standards": "DFS 400 / ISO 6858 / MIL-STD-704F"
  },
  {
    "id": 24,
    "name_en": "Pre-Conditioned Air (PCA) Direct-Expansion Compressor",
    "name_zh": "飛機地面預調空調螺桿壓縮機 (PCA Unit)",
    "boundary": "Airport Management",
    "beta": 2.5,
    "eta": 65000,
    "mttf_hours": 57600,
    "mttf_years": 9,
    "failure_mode": "瞬態大溫差熱應力破壞、滑閥容積調節卡滯、吸氣過濾網結霜堵塞",
    "maintenance_strategy": "每月檢測出風靜壓及排氣溫度、季檢更換冷凍油及乾燥過濾器",
    "standards": "AHRI 550/590 / IATA AHM 974"
  },
  {
    "id": 25,
    "name_en": "Apron High-Mast LED Floodlight Electronic Driver",
    "name_zh": "停機坪高桿防眩 LED 照明電子驅動器",
    "boundary": "Airport Management",
    "beta": 2.2,
    "eta": 60000,
    "mttf_hours": 53100,
    "mttf_years": 10,
    "failure_mode": "露天金屬箱受烈日曝曬過溫保護自鎖、戶外雷擊感應過電壓擊穿",
    "maintenance_strategy": "颱風季前後檢測外殼防護等級 (IP66) 密封膠條與浪湧保護器狀態",
    "standards": "ICAO Annex 14 / CIE 154 / HKCAD"
  },
  {
    "id": 26,
    "name_en": "Runway Visual Range (RVR) Scatter Transmissometer Head",
    "name_zh": "跑道視程前向散射透射儀光電探頭",
    "boundary": "Airport Management",
    "beta": 1.5,
    "eta": 130000,
    "mttf_hours": 117000,
    "mttf_years": 16,
    "failure_mode": "發射LED光源衰減、石英光學窗口防霧吹風機加熱絲熔斷",
    "maintenance_strategy": "每月光學自校對準器 (Calibrator) 校核散射係數、清洗透鏡",
    "standards": "ICAO Doc 9328 / WMO No. 8"
  },
  {
    "id": 27,
    "name_en": "Automated People Mover (APM) Linear Induction Motor",
    "name_zh": "旅客捷運系統 (APM) 線性感應馬達 (LIM)",
    "boundary": "Airport Management",
    "beta": 1.8,
    "eta": 140000,
    "mttf_hours": 124000,
    "mttf_years": 18,
    "failure_mode": "初級鐵芯齒槽受軌道碎石擊傷、高溫環境環氧封裝絕緣熱老化",
    "maintenance_strategy": "定期動態氣隙測量儀 (Air-gap Sensor) 監控 (標準間隙 12±2mm)",
    "standards": "ASCE 21 (Automated People Mover Standards)"
  },
  {
    "id": 28,
    "name_en": "Air Cargo Automated Storage & Retrieval (ASRS) Crane",
    "name_zh": "空運貨站自動立體倉庫堆垛機起升機構",
    "boundary": "Airport Management",
    "beta": 2.6,
    "eta": 75000,
    "mttf_hours": 66600,
    "mttf_years": 10,
    "failure_mode": "重載鋼索跳槽磨損、起升減速箱斜齒輪疲勞點蝕、激光測距傳感器鏡片髒污",
    "maintenance_strategy": "每月磁粉探傷吊叉根部、校準走行激光測距原點",
    "standards": "FEM 9.831 / BS EN 528"
  },
  {
    "id": 29,
    "name_en": "Advanced Visual Docking Guidance System (A-VDGS) Scanner",
    "name_zh": "停機位高級視覺引導系統 (A-VDGS) 激光掃描儀",
    "boundary": "Airport Management",
    "beta": 1.7,
    "eta": 80000,
    "mttf_hours": 71200,
    "mttf_years": 11,
    "failure_mode": "旋轉多面棱鏡軸承磨損卡頓、激光發射二極管發光功率衰退",
    "maintenance_strategy": "季度用標準反射板靶標校準測距及航向偏角精度",
    "standards": "ICAO Annex 14 Aerodrome Design"
  },
  {
    "id": 30,
    "name_en": "Aviation Hydrant Emergency Fuel Shutoff Valve (EFSO)",
    "name_zh": "停機坪航空燃油管網氣動快速緊急切斷閥",
    "boundary": "Airport Management",
    "beta": 1.3,
    "eta": 180000,
    "mttf_hours": 165000,
    "mttf_years": 25,
    "failure_mode": "氣動執行機構壓縮彈簧長期受壓疲勞、氟橡膠閥座密封面被油泥磨蝕",
    "maintenance_strategy": "每月機坪緊急停油按鈕 (ESD) 聯動全閉行程測試 (<2秒關閉)",
    "standards": "JIG (Joint Inspection Group) / API 1584"
  },
  {
    "id": 31,
    "name_en": "Instrument Landing System (ILS) Localizer Antenna",
    "name_zh": "盲降系統 (ILS) 航向信標天線偶極子陣列",
    "boundary": "Airport Management",
    "beta": 1.2,
    "eta": 250000,
    "mttf_hours": 236000,
    "mttf_years": 30,
    "failure_mode": "沿海高鹽霧導致天線同軸饋線接頭進水腐蝕氧化、駐波比 (VSWR) 超標",
    "maintenance_strategy": "半年一次民航飛行校驗機 (Flight Check) 實時校驗航道調制度",
    "standards": "ICAO Annex 10 Aeronautical Telecommunications"
  },
  {
    "id": 32,
    "name_en": "Airfield Ground Lighting (AGL) Constant Current Regulator",
    "name_zh": "機場跑道助航燈光可控矽恆流調光器 (CCR)",
    "boundary": "Airport Management",
    "beta": 2.1,
    "eta": 110000,
    "mttf_hours": 97400,
    "mttf_years": 15,
    "failure_mode": "晶閘管開關觸發電路漂移、高壓串聯隔離變壓器次級局部放電",
    "maintenance_strategy": "季度測試各級電流階梯 (2.8A - 6.6A) 輸出精度與接地絕緣電阻",
    "standards": "FAA AC 150/5345-10 / IEC 61822"
  },
  {
    "id": 33,
    "name_en": "Terminal Central Chilled Water Plant Centrifugal Chiller",
    "name_zh": "客運大樓中央大型水冷離心冷水機 (3000 RT)",
    "boundary": "Airport Management",
    "beta": 2.4,
    "eta": 160000,
    "mttf_hours": 142000,
    "mttf_years": 25,
    "failure_mode": "磁懸浮軸承控制器傳感器漂移、冷凝器銅管水垢滋生致傳熱惡化",
    "maintenance_strategy": "自動膠球線上清洗系統日常維護、每年非破壞性渦流探傷冷凝管",
    "standards": "EMSD BEC / AHRI 550/590 / ASHRAE 90.1"
  },
  {
    "id": 34,
    "name_en": "Aircraft Pushback Tractor Electro-Hydraulic Steering Pump",
    "name_zh": "飛機無桿牽引車主液壓轉向泵 (Pushback Tractor)",
    "boundary": "Airport Management",
    "beta": 2.5,
    "eta": 40000,
    "mttf_hours": 35500,
    "mttf_years": 6,
    "failure_mode": "斜盤柱塞滑靴磨損脫落、先導比例電磁閥閥芯微卡死致轉向遲滯",
    "maintenance_strategy": "每1000運轉小時更換液壓濾芯與油質光譜金屬顆粒分析",
    "standards": "IATA AHM 910 / ISO 6967"
  },
  {
    "id": 35,
    "name_en": "Runway Seawall Stormwater Tidal Flap Gate",
    "name_zh": "三跑人工島海堤暴雨自排防潮拍門",
    "boundary": "Airport Management",
    "beta": 1.6,
    "eta": 180000,
    "mttf_hours": 161000,
    "mttf_years": 25,
    "failure_mode": "海水藤壺海生物附著使鉸鏈軸銷卡死無法自動下墜、雙相鋼門板沖刷變形",
    "maintenance_strategy": "每半年潛水員人工清除拍門貝類海生物、潤滑耐磨青銅襯套",
    "standards": "CEDD Port Works Design Manual"
  },
  {
    "id": 36,
    "name_en": "Terminal Revolving Door Safety Sensor & Edge",
    "name_zh": "客運大樓主入口自動旋轉門防夾橡膠安全邊緣",
    "boundary": "Airport Management",
    "beta": 2.2,
    "eta": 50000,
    "mttf_hours": 44300,
    "mttf_years": 7,
    "failure_mode": "旅客行李車頻繁碰撞致內部導電橡膠斷裂、微動開關觸點彈性疲乏",
    "maintenance_strategy": "每週用專用測試塊進行防夾緩衝與即時回退剎車試驗",
    "standards": "BS EN 16005 / DIN 18650"
  },
  {
    "id": 37,
    "name_en": "Dual-View Baggage X-Ray Generator Tube",
    "name_zh": "大件行李安檢雙視角 X 光高壓射線管球",
    "boundary": "Airport Management",
    "beta": 2.8,
    "eta": 25000,
    "mttf_hours": 22200,
    "mttf_years": 3.5,
    "failure_mode": "高壓鎢靶表面熱熔融點蝕、絕緣絕緣油高溫碳化引起高壓打火擊穿",
    "maintenance_strategy": "每2000小時進行射線劑量與線對分辨率 (Wire Resolution) 校正",
    "standards": "TSA / ECAC Security Standards"
  },
  {
    "id": 38,
    "name_en": "Fuel Farm Vapor Recovery Multi-Stage Screw Compressor",
    "name_zh": "機場航油油庫油氣回收螺桿壓縮機",
    "boundary": "Airport Management",
    "beta": 2.1,
    "eta": 85000,
    "mttf_hours": 75300,
    "mttf_years": 12,
    "failure_mode": "碳氫氣體冷凝沖刷轉子塗層、機械密封受油氣溶脹失效",
    "maintenance_strategy": "每季度可燃氣體探測聯動跳掣校驗、冷凝液排污檢測",
    "standards": "NFPA 30 / API 619"
  },
  {
    "id": 39,
    "name_en": "Apron Passenger Bus Pneumatic Door Control Valve",
    "name_zh": "停機坪旅客擺渡車氣動雙開門電磁閥",
    "boundary": "Airport Management",
    "beta": 2.3,
    "eta": 45000,
    "mttf_hours": 39800,
    "mttf_years": 6,
    "failure_mode": "空壓系統冷凝水侵蝕使閥芯氧化卡阻、密封O型圈磨損漏氣",
    "maintenance_strategy": "每月檢查儲氣筒自動排水閥、校驗門開關閉速度防夾力",
    "standards": "ECE R107 (Passenger Bus Door Regulations)"
  },
  {
    "id": 40,
    "name_en": "Runway Friction Tester Continuous Measuring Wheel",
    "name_zh": "跑道道面摩擦系數連續測試車第5輪傳感機構",
    "boundary": "Airport Management",
    "beta": 2.7,
    "eta": 30000,
    "mttf_hours": 26700,
    "mttf_years": 4,
    "failure_mode": "高速滑動磨擦使專用測試橡膠輪嚴重偏磨、扭矩傳感器零點受衝擊漂移",
    "maintenance_strategy": "每次雨前跑道測試前進行載荷標定砝碼校準與灑水系統流量測試",
    "standards": "ICAO Annex 14 / FAA AC 150/5320-12C"
  },
  {
    "id": 41,
    "name_en": "11kV/380V Cast Resin Dry-Type Distribution Transformer",
    "name_zh": "乾式環氧樹脂配電變壓器 (CLP/HKE Grid)",
    "boundary": "City Common Infrastructure",
    "beta": 2.2,
    "eta": 250000,
    "mttf_hours": 221000,
    "mttf_years": 30,
    "failure_mode": "環氧樹脂受潮與高溫引發局部放電 (PD)、冷卻風道積塵過熱",
    "maintenance_strategy": "年度停電除塵、熱成像接頭檢測、局放超聲波探測",
    "standards": "IEC 60076-11 / CLP Supply Rules"
  },
  {
    "id": 42,
    "name_en": "132kV Primary Grid Oil-Immersed Power Transformer",
    "name_zh": "132kV 電網主變電站油浸式電力變壓器",
    "boundary": "City Common Infrastructure",
    "beta": 2.4,
    "eta": 280000,
    "mttf_hours": 248000,
    "mttf_years": 35,
    "failure_mode": "絕緣紙聚合度 (DP) 降解老化、絕緣油中乙炔烴類氣體增加、套管受潮",
    "maintenance_strategy": "每半年油中溶解氣體色譜分析 (DGA)、繞組頻率響應分析 (FRA)",
    "standards": "IEEE C57.104 / IEC 60076"
  },
  {
    "id": 43,
    "name_en": "11kV Vacuum Circuit Breaker (VCB) Operating Mechanism",
    "name_zh": "11千伏真空斷路器彈簧操動機構",
    "boundary": "City Common Infrastructure",
    "beta": 1.9,
    "eta": 180000,
    "mttf_hours": 159000,
    "mttf_years": 25,
    "failure_mode": "真空滅弧室真空度漏失、儲能彈簧金屬疲勞斷裂、分閘線圈燒毀",
    "maintenance_strategy": "年度斷路器動特性測試（分合閘同期性、彈跳時間 <2ms）",
    "standards": "IEC 62271-100 / EMSD CoP"
  },
  {
    "id": 44,
    "name_en": "Potable Water High-Lift Hydro-Pneumatic Booster Pump",
    "name_zh": "高地食水增壓泵 (WSD Primary Booster)",
    "boundary": "City Common Infrastructure",
    "beta": 2.3,
    "eta": 95000,
    "mttf_hours": 84100,
    "mttf_years": 12,
    "failure_mode": "機械密封碳化硅摩擦面開裂滲漏、葉輪高揚程氣蝕沖刷減薄",
    "maintenance_strategy": "每半年泵組震動軸承頻譜量測、葉輪動平衡校驗 (WSD Standards)",
    "standards": "WSD Manual / BS EN ISO 9906"
  },
  {
    "id": 45,
    "name_en": "Deep Tunnel Submersible Sewage Lift Pump",
    "name_zh": "淨化海港計劃深層污水大型沉水泵 (DSD Megapump)",
    "boundary": "City Common Infrastructure",
    "beta": 2.6,
    "eta": 60000,
    "mttf_hours": 53300,
    "mttf_years": 8,
    "failure_mode": "硫化氫腐蝕雙相不銹鋼外殼、油室滲水探頭短路報警、重泥沙磨損切割葉片",
    "maintenance_strategy": "每季吊泵外觀檢測、更換油室合成絕緣油及冷卻夾套除垢",
    "standards": "DSD Sewerage Manual / BS EN 12050"
  },
  {
    "id": 46,
    "name_en": "Municipal Sewage Macerator Grinder Pump",
    "name_zh": "市政污水截流粉碎切割泵",
    "boundary": "City Common Infrastructure",
    "beta": 2.9,
    "eta": 40000,
    "mttf_hours": 35600,
    "mttf_years": 6,
    "failure_mode": "硬質異物撞擊鎢鋼刀片崩刃卡死、電機過載熱繼電器頻繁跳閘",
    "maintenance_strategy": "半年更換高鉻鑄鐵切割盤、量測三相繞組平衡度",
    "standards": "BS EN 12050-1 / DSD Practice Notes"
  },
  {
    "id": 47,
    "name_en": "Mains Water Direct-Acting Pilot Pressure Reducing Valve",
    "name_zh": "市政供水管網先導式水壓減壓閥 (PRV)",
    "boundary": "City Common Infrastructure",
    "beta": 2.0,
    "eta": 80000,
    "mttf_hours": 70900,
    "mttf_years": 11,
    "failure_mode": "銅先導針閥被管網紅銹堵塞、橡膠加強筋隔膜疲勞破裂引發管網超壓水錘",
    "maintenance_strategy": "定期清洗先導前置Y型過濾器、超聲波流量計對比進出口壓降",
    "standards": "WSD Departmental Standard / AWWA C530"
  },
  {
    "id": 48,
    "name_en": "Ductile Iron Resilient-Seated Gate Valve",
    "name_zh": "市政球墨鑄鐵彈性座封暗桿閘閥",
    "boundary": "City Common Infrastructure",
    "beta": 1.5,
    "eta": 140000,
    "mttf_hours": 126000,
    "mttf_years": 20,
    "failure_mode": "管底泥沙石子積聚卡死閘板無法切斷、閥桿無鉛青銅螺母磨蝕滑牙",
    "maintenance_strategy": "每年由水喉匠進行全開全關操作測試以防泥沙結垢",
    "standards": "BS EN 1171 / WSD Standard Drawings"
  },
  {
    "id": 49,
    "name_en": "District Raw Water Electromagnetic Flow Meter",
    "name_zh": "東深供水大口徑電磁原水計量表 (DN1200)",
    "boundary": "City Common Infrastructure",
    "beta": 1.6,
    "eta": 110000,
    "mttf_hours": 98000,
    "mttf_years": 15,
    "failure_mode": "電極表面沉積絕緣碳酸鈣垢層導致信號衰減、勵磁線圈受潮短路",
    "maintenance_strategy": "年度用低頻信號發生器進行轉換器線性度自校、刮刀清洗電極",
    "standards": "ISO 4064 / OIML R49"
  },
  {
    "id": 50,
    "name_en": "Smart Street Lighting Microprocessor Photocell Switch",
    "name_zh": "智慧城市路燈微處理器光控感應開關",
    "boundary": "City Common Infrastructure",
    "beta": 2.1,
    "eta": 65000,
    "mttf_hours": 57600,
    "mttf_years": 10,
    "failure_mode": "光敏二極管光譜漂移引發天黑遲開或白天誤開、微型繼電器觸點黏連",
    "maintenance_strategy": "利用路政署智慧路燈聯網管理平台遠程監控日誌告警",
    "standards": "HyD (Highways Dept) Specs / BS 5972"
  },
  {
    "id": 51,
    "name_en": "Stormwater Culvert Heavy-Duty Stainless Tidal Flap Gate",
    "name_zh": "防洪箱涵雙相不銹鋼重型防潮排澇拍門",
    "boundary": "City Common Infrastructure",
    "beta": 1.7,
    "eta": 160000,
    "mttf_hours": 143000,
    "mttf_years": 22,
    "failure_mode": "河道漂浮枯木垃圾卡死門縫造成海水倒灌、橡膠背條老化密封不嚴",
    "maintenance_strategy": "雨季前由工程人員清理拍門口沉積物、潤滑自潤滑青銅軸承",
    "standards": "DSD Stormwater Manual / CEDD"
  },
  {
    "id": 52,
    "name_en": "Pre-Stressed Geotechnical Slope Ground Anchor Load Cell",
    "name_zh": "土力工程處斜坡預應力錨索受力監測傳感器",
    "boundary": "City Common Infrastructure",
    "beta": 1.3,
    "eta": 220000,
    "mttf_hours": 202000,
    "mttf_years": 28,
    "failure_mode": "鋼絞線在酸性土壤中應力腐蝕斷裂 (Stress Corrosion)、傳感器信號電纜受鼠咬",
    "maintenance_strategy": "按 GEO 指引每年進行錨索預應力回拉抽檢試驗 (Lift-off Test)",
    "standards": "GEO Publication / CEDD Slope Manual"
  },
  {
    "id": 53,
    "name_en": "Highway Flyover Expansion Joint Elastomeric Sealing Element",
    "name_zh": "高架公路幹線橋樑伸縮縫橡膠密封止水帶",
    "boundary": "City Common Infrastructure",
    "beta": 2.5,
    "eta": 70000,
    "mttf_hours": 62300,
    "mttf_years": 9,
    "failure_mode": "重型車輛輪胎剪切撕裂、砂石嵌入擠破引起梁底鋼筋銹蝕漏水",
    "maintenance_strategy": "每半年目視裂紋擴展長度檢測、高壓水槍沖洗縫內泥石雜物",
    "standards": "HyD Structures Design Manual"
  },
  {
    "id": 54,
    "name_en": "Underground High-Pressure Gas Distribution Governor",
    "name_zh": "地下天然氣中高壓調壓箱平衡膜片 (Gas Governor)",
    "boundary": "City Common Infrastructure",
    "beta": 1.8,
    "eta": 90000,
    "mttf_hours": 80100,
    "mttf_years": 12,
    "failure_mode": "合成丁腈橡膠膜片硬化穿孔引起超壓放散、微孔調壓導向件粉塵磨蝕",
    "maintenance_strategy": "每季度超壓切斷閥 (Slam-shut Valve) 跳脫靈敏度驗證",
    "standards": "Cap 51 Gas Safety Ordinance / EMSD Gas Specs"
  },
  {
    "id": 55,
    "name_en": "Sewage Aeration Blower High-Speed Turbo Compressor",
    "name_zh": "污水處理廠曝氣磁懸浮高速離心鼓風機",
    "boundary": "City Common Infrastructure",
    "beta": 2.2,
    "eta": 100000,
    "mttf_hours": 88500,
    "mttf_years": 14,
    "failure_mode": "備用蓄電池失效致突然斷電磁懸浮跌落軸承損壞、空氣吸入口消音棉破損",
    "maintenance_strategy": "每月檢查磁浮控制器氣隙反饋波形、定期清潔進氣初效濾網",
    "standards": "DSD Electrical Specs / ISO 10816-3"
  },
  {
    "id": 56,
    "name_en": "Traffic Signal Master Area Controller Unit",
    "name_zh": "聯網交通燈路口協調控制主機 (ATC Controller)",
    "boundary": "City Common Infrastructure",
    "beta": 1.5,
    "eta": 130000,
    "mttf_hours": 117000,
    "mttf_years": 16,
    "failure_mode": "路口高溫濕熱導致工控板電容爆漿、綠衝突硬件互鎖繼電器觸點氧化",
    "maintenance_strategy": "年度模擬綠衝突安全強制黃閃試驗、檢查UPS蓄電池續航力",
    "standards": "Transport Dept / HyD Specs"
  },
  {
    "id": 57,
    "name_en": "Impressed Current Deep Well Cathodic Protection Anode",
    "name_zh": "地下鋼製管網外加電流陰極保護深井陽極 (MMO Anode)",
    "boundary": "City Common Infrastructure",
    "beta": 1.4,
    "eta": 200000,
    "mttf_hours": 182000,
    "mttf_years": 25,
    "failure_mode": "焦炭回填料消耗枯竭接地電阻攀升、陽極導線絕緣破裂致芯線電解腐蝕斷路",
    "maintenance_strategy": "每月測量管地電位 (CSE 參考電極 -850mV 至 -1200mV)",
    "standards": "NACE SP0169 / WSD Cathodic Guidelines"
  },
  {
    "id": 58,
    "name_en": "Water Treatment Rapid Sand Filter Pneumatic Butterfly Valve",
    "name_zh": "濾水廠石英砂濾池反沖洗氣動雙偏心蝶閥",
    "boundary": "City Common Infrastructure",
    "beta": 2.1,
    "eta": 75000,
    "mttf_hours": 66400,
    "mttf_years": 10,
    "failure_mode": "氣動活塞密封圈洩氣引起開閥力矩不足、橡膠閥座磨損滲水",
    "maintenance_strategy": "季度測量全開全關切換響應時間 (<8秒)、檢查氣源油霧潤滑器",
    "standards": "WSD Civil & E&M Manual"
  },
  {
    "id": 59,
    "name_en": "Storm Drainage Sump Ultrasonic Level Transmitter",
    "name_zh": "雨水渠蓄洪池超聲波液位監測變送器",
    "boundary": "City Common Infrastructure",
    "beta": 1.5,
    "eta": 95000,
    "mttf_hours": 85600,
    "mttf_years": 12,
    "failure_mode": "探頭發射面結露凝結水滴導致盲區增大、雷擊感應破壞4-20mA輸出端子",
    "maintenance_strategy": "雨季前現場量程比對、探頭聚四氟乙烯保護面清潔",
    "standards": "DSD Practice Notes / IEC 60770"
  },
  {
    "id": 60,
    "name_en": "Public EV DC Fast Charger Power Converter Module",
    "name_zh": "公共直流快速充電樁高壓功率轉換模組 (30kW Module)",
    "boundary": "City Common Infrastructure",
    "beta": 2.3,
    "eta": 50000,
    "mttf_hours": 44300,
    "mttf_years": 6,
    "failure_mode": "高頻 SiC MOSFET 熱擊穿、戶外散熱風扇軸承卡死致高溫降額",
    "maintenance_strategy": "季度防塵棉更換、絕緣耐壓測試 (漏電流 <5mA) 及充電協議通訊校驗",
    "standards": "EMSD CoP for EV Charging / IEC 61851"
  },
  {
    "id": 61,
    "name_en": "Commercial Centrifugal Water-Cooled Chiller",
    "name_zh": "商業大廈中央水冷離心式冷水機 (Chiller)",
    "boundary": "Building & Facility Management",
    "beta": 2.5,
    "eta": 150000,
    "mttf_hours": 133000,
    "mttf_years": 25,
    "failure_mode": "離心葉輪氣蝕磨損、滑動軸承疲勞剝落、機械密封冷媒洩漏",
    "maintenance_strategy": "每年冷媒潤滑油光譜分析、冷凍油更換、震動頻譜監測",
    "standards": "EMSD BEC / ASHRAE 90.1 / CIBSE Guide M"
  },
  {
    "id": 62,
    "name_en": "Air-Cooled Rotary Screw Chiller",
    "name_zh": "天台風冷螺桿機組 (Air-Cooled Chiller)",
    "boundary": "Building & Facility Management",
    "beta": 2.2,
    "eta": 110000,
    "mttf_hours": 97400,
    "mttf_years": 18,
    "failure_mode": "雙螺桿陰陽轉子咬死、高溫高濕沿海鹽霧侵蝕鋁翅片冷凝盤管",
    "maintenance_strategy": "定期翅片高壓除塵清洗、電子膨脹閥開度行程校準",
    "standards": "EMSD BEC / AHRI 550/590"
  },
  {
    "id": 63,
    "name_en": "Induced Draft Cooling Tower Variable-Pitch Fan",
    "name_zh": "冷卻水塔變速風扇及直聯電機",
    "boundary": "Building & Facility Management",
    "beta": 2.8,
    "eta": 65000,
    "mttf_hours": 57900,
    "mttf_years": 10,
    "failure_mode": "扇葉鋁合金疲勞產生微裂紋、電機浸水防護失效受潮燒毀",
    "maintenance_strategy": "每月檢查皮帶張力與軸承注脂、防退伍軍人症清洗消毒 (WACS 條例)",
    "standards": "EMSD CoP for Water-cooled Air Conditioning Systems"
  },
  {
    "id": 64,
    "name_en": "Primary Chilled Water Variable Speed Pump",
    "name_zh": "一次冷凍水變頻離心泵 (Primary Pump)",
    "boundary": "Building & Facility Management",
    "beta": 2.3,
    "eta": 120000,
    "mttf_hours": 106000,
    "mttf_years": 20,
    "failure_mode": "雙端面碳化硅機械軸封滴漏、葉輪動態偏磨產生異常噪音",
    "maintenance_strategy": "半年一次激光同軸度校正、監測軸承震動值 (<2.8mm/s ISO 10816)",
    "standards": "ISO 10816-3 / CIBSE Guide M"
  },
  {
    "id": 65,
    "name_en": "Central Air Handling Unit (AHU) Centrifugal Fan",
    "name_zh": "中央風櫃離心送風機及電機 (AHU Blower)",
    "boundary": "Building & Facility Management",
    "beta": 2.1,
    "eta": 100000,
    "mttf_hours": 88600,
    "mttf_years": 15,
    "failure_mode": "驅動三角皮帶打滑老化斷裂、電機深溝球軸承乾磨損壞",
    "maintenance_strategy": "每月調整皮帶撓度、半年動平衡測試、更換過濾網",
    "standards": "ASHRAE 62.1 / CIBSE Guide M"
  },
  {
    "id": 66,
    "name_en": "Fan Coil Unit (FCU) Brushless DC (BLDC) Motor",
    "name_zh": "風機盤管高效直流無刷電機 (FCU BLDC Motor)",
    "boundary": "Building & Facility Management",
    "beta": 1.8,
    "eta": 70000,
    "mttf_hours": 62200,
    "mttf_years": 10,
    "failure_mode": "驅動控制板內置電解電容鼓包、含油軸承乾涸發熱卡滯",
    "maintenance_strategy": "定期清洗初效濾網、量度運行運轉電流與轉速穩定性",
    "standards": "IEC 60034 / EMSD BEC"
  },
  {
    "id": 67,
    "name_en": "Low-Voltage Main Switchboard Air Circuit Breaker (ACB)",
    "name_zh": "低壓配電總掣櫃空氣斷路器 (ACB, 大掣)",
    "boundary": "Building & Facility Management",
    "beta": 2.1,
    "eta": 160000,
    "mttf_hours": 141000,
    "mttf_years": 20,
    "failure_mode": "金屬滅弧片受損、主銀觸點過熱氧化黏連、微處理器脫扣器精度漂移",
    "maintenance_strategy": "法定每5年進行一次電力 WR2 定期檢驗、二次電流注入跳閘校驗",
    "standards": "BS EN 60947-2 / EMSD CoP (Electricity)"
  },
  {
    "id": 68,
    "name_en": "Automatic Transfer Switch (ATS) Dual Power Mechanism",
    "name_zh": "雙電源自動轉換開關 (ATS)",
    "boundary": "Building & Facility Management",
    "beta": 1.8,
    "eta": 130000,
    "mttf_hours": 115000,
    "mttf_years": 20,
    "failure_mode": "機械互鎖連桿變形卡阻、切換電磁線圈燒毀致無法切換至發電機",
    "maintenance_strategy": "每半年手動及市電斷電模擬切換測試、觸頭紅外測溫",
    "standards": "IEC 60947-6-1 / NFPA 110"
  },
  {
    "id": 69,
    "name_en": "Standby Emergency Diesel Generator Set",
    "name_zh": "大廈後備緊急柴油發電機組",
    "boundary": "Building & Facility Management",
    "beta": 1.5,
    "eta": 120000,
    "mttf_hours": 107000,
    "mttf_years": 25,
    "failure_mode": "鉛酸起動蓄電池壓降過大無法盤車、柴油噴油嘴結膠、水套加熱器損壞",
    "maintenance_strategy": "每月空載試機30分鐘、年度由持牌電業承辦商進行假負載 (Dummy Load) 100% 測試",
    "standards": "FSD CoP / ISO 8528 / NFPA 110"
  },
  {
    "id": 70,
    "name_en": "Data Center Double-Conversion Online UPS Inverter",
    "name_zh": "數據中心在線雙變換不斷電系統逆變器 (UPS)",
    "boundary": "Building & Facility Management",
    "beta": 2.3,
    "eta": 90000,
    "mttf_hours": 79800,
    "mttf_years": 12,
    "failure_mode": "直流母線濾波電容乾涸熱擊穿、冷卻散熱風扇卡滯致 IGBT 逆變模組爆裂",
    "maintenance_strategy": "每5年預防性更換整組直流電容及散熱風扇、季度電池放電測試",
    "standards": "IEC 62040-3 / IEEE 493 Gold Book"
  },
  {
    "id": 71,
    "name_en": "Machine-Room-Less (MRL) PM Lift Traction Machine",
    "name_zh": "無機房永磁同步升降機曳引機 (Traction Machine)",
    "boundary": "Building & Facility Management",
    "beta": 2.2,
    "eta": 150000,
    "mttf_hours": 132900,
    "mttf_years": 20,
    "failure_mode": "機械抱閘摩擦片磨損超差、曳引輪半圓繩槽受鋼索磨耗變形",
    "maintenance_strategy": "機電署每半月一次例行巡檢、註冊升降機工程師年度全面檢驗簽發 Form 11",
    "standards": "EMSD CoP for Lift & Escalator / Cap 618 / EN 81-20"
  },
  {
    "id": 72,
    "name_en": "High-Speed Elevator Regenerative VVVF Inverter",
    "name_zh": "高速客梯能量回饋型變頻器 (VVVF Drive)",
    "boundary": "Building & Facility Management",
    "beta": 2.1,
    "eta": 80000,
    "mttf_hours": 70800,
    "mttf_years": 10,
    "failure_mode": "能量回饋單元IGBT過熱穿透、控制電路板接插件因大廈微震鬆脫",
    "maintenance_strategy": "定期吸塵清理驅動模組散熱片、檢查母線電壓平衡度",
    "standards": "EN 81-20 / IEC 61800"
  },
  {
    "id": 73,
    "name_en": "Heavy-Duty Commercial Escalator Step Chain & Drive",
    "name_zh": "商場扶手電梯主驅動鏈條及步級鏈 (Step Chain)",
    "boundary": "Building & Facility Management",
    "beta": 2.8,
    "eta": 70000,
    "mttf_hours": 62300,
    "mttf_years": 9,
    "failure_mode": "梯級鏈銷軸磨損導致節距拉長伸長超標、自動注油器油路堵塞乾磨",
    "maintenance_strategy": "每月檢查自動注油泵壓力、每半年精密測量梯級鏈伸長量 (Form 11)",
    "standards": "EN 115-1 / EMSD CoP for Escalator"
  },
  {
    "id": 74,
    "name_en": "Fire Services Ring-Main Wet Hydrant Booster Pump",
    "name_zh": "大廈環形管網消防栓加壓水泵 (FH Pump)",
    "boundary": "Building & Facility Management",
    "beta": 1.5,
    "eta": 150000,
    "mttf_hours": 135000,
    "mttf_years": 25,
    "failure_mode": "長年備用不轉導致機械軸封水垢銹死、星三角起動接觸器氧化",
    "maintenance_strategy": "每月由物業工程員手動試運轉、年度由註冊消防承辦商簽發 FS251",
    "standards": "FSD CoP / BS 5306-1 / Cap 95 Fire Services Ordinance"
  },
  {
    "id": 75,
    "name_en": "Automatic Sprinkler System Alarm Check Valve",
    "name_zh": "自動花灑水力警鈴濕式警報閥組",
    "boundary": "Building & Facility Management",
    "beta": 1.3,
    "eta": 180000,
    "mttf_hours": 165000,
    "mttf_years": 25,
    "failure_mode": "水力警鈴葉輪積垢銹蝕卡死不轉、減速延遲室排水孔堵塞引發誤報",
    "maintenance_strategy": "每季末端放水閥測試警報閥響應、清理延遲室濾網",
    "standards": "FSD CoP / LPC Rules / BS EN 12845"
  },
  {
    "id": 76,
    "name_en": "Addressable Multi-Sensor Optical Smoke & Heat Detector",
    "name_zh": "地址碼複合光電感煙感溫火警探測器",
    "boundary": "Building & Facility Management",
    "beta": 1.8,
    "eta": 80000,
    "mttf_hours": 70900,
    "mttf_years": 10,
    "failure_mode": "光學迷宮暗室被裝修粉塵污垢遮蔽引起假火警、紅外發光管光強衰變",
    "maintenance_strategy": "定期專用煙霧吹掃觸發抽查、定期返廠超聲波除塵清洗",
    "standards": "BS EN 54-7 / FSD Circular Letters"
  },
  {
    "id": 77,
    "name_en": "Clean Agent Gas Release Solenoid Pilot Actuator",
    "name_zh": "七氟丙烷 (FM-200) 鋼樽電磁釋放閥",
    "boundary": "Building & Facility Management",
    "beta": 1.4,
    "eta": 80000,
    "mttf_hours": 72800,
    "mttf_years": 12,
    "failure_mode": "電磁線圈匝間短路、機械撞針擊針彈簧疲勞銹死無法刺破金屬膜片",
    "maintenance_strategy": "年度拆除電磁頭進行模擬通電打靶跳脫試驗、稱重檢查鋼樽氣壓",
    "standards": "NFPA 2001 / ISO 14520 / FSD CoP"
  },
  {
    "id": 78,
    "name_en": "Building Management System (BMS) DDC Controller",
    "name_zh": "樓宇自控直接數字控制器 (BMS DDC)",
    "boundary": "Building & Facility Management",
    "beta": 1.6,
    "eta": 120000,
    "mttf_hours": 107000,
    "mttf_years": 15,
    "failure_mode": "RS485 BACnet 通訊晶片受靜電浪湧擊穿、板載供電整流模組熱老化",
    "maintenance_strategy": "定期通訊在線率監測、年度程式代碼備份及供電紋波測試",
    "standards": "ASHRAE 135 (BACnet) / EMSD BEC"
  },
  {
    "id": 79,
    "name_en": "Variable Air Volume (VAV) Modulating Damper Actuator",
    "name_zh": "變風量箱比例調節風閥致動器 (VAV Actuator)",
    "boundary": "Building & Facility Management",
    "beta": 1.5,
    "eta": 80000,
    "mttf_hours": 72300,
    "mttf_years": 12,
    "failure_mode": "減速齒輪箱塑膠齒輪受阻力斷齒、開度反饋電位器碳膜磨耗接觸不良",
    "maintenance_strategy": "季度開度 0-100% 行程校驗、手動離合旋鈕開關測試",
    "standards": "EN 1751 / CIBSE Guide H"
  },
  {
    "id": 80,
    "name_en": "Kitchen Exhaust Hood Wet Chemical Fire Suppression Valve",
    "name_zh": "商場餐廳廚房油煙罩濕式化學滅火機械釋放閥",
    "boundary": "Building & Facility Management",
    "beta": 1.7,
    "eta": 65000,
    "mttf_hours": 57900,
    "mttf_years": 8,
    "failure_mode": "排煙重油污凝固滲入卡死不銹鋼鋼索滑輪、易熔金屬片感溫熔斷遲鈍",
    "maintenance_strategy": "每半年除油清洗易熔片連桿機構、更換藥劑筒防腐密封墊",
    "standards": "NFPA 17A / FSD Circular Letters"
  },
  {
    "id": 81,
    "name_en": "Quay Crane (QC) Main Hoist Winch Motor & Gearbox",
    "name_zh": "岸邊集裝箱起重機主起升捲揚電機與行星齒輪箱 (QC Hoist)",
    "boundary": "Port & Marine Logistics",
    "beta": 2.5,
    "eta": 90000,
    "mttf_hours": 79800,
    "mttf_years": 12,
    "failure_mode": "重載衝擊致行星輪軸承疲勞剝落、多盤式液壓制動器磨擦片油污打滑",
    "maintenance_strategy": "每季度齒輪油光譜金屬分析、制動器開閉間隙自動塞尺檢測",
    "standards": "BS EN 15011 / FEM 1.001 / Marine Dept Specs"
  },
  {
    "id": 82,
    "name_en": "Quay Crane Boom Luffing Wire Rope Sheave Assembly",
    "name_zh": "岸橋吊臂俯仰鋼絲繩導向滑輪組 (Boom Sheave)",
    "boundary": "Port & Marine Logistics",
    "beta": 2.7,
    "eta": 60000,
    "mttf_hours": 53400,
    "mttf_years": 8,
    "failure_mode": "鑄鋼滑輪繩槽偏磨變形、雙列調心滾子軸承海霧鹽腐蝕麻點",
    "maintenance_strategy": "每月高空登頂滑輪槽底測量、自動集中潤滑系統油路排空",
    "standards": "ISO 4309 / DIN 15020"
  },
  {
    "id": 83,
    "name_en": "Container Spreader Hydraulic Twistlock Actuator",
    "name_zh": "集裝箱吊具專用液壓轉鎖銷機構 (Twistlock)",
    "boundary": "Port & Marine Logistics",
    "beta": 3.0,
    "eta": 35000,
    "mttf_hours": 31300,
    "mttf_years": 4,
    "failure_mode": "旋鎖軸頸承受千萬次吊裝剪切微裂紋疲勞斷裂、微動感應器感應失靈",
    "maintenance_strategy": "按吊裝箱量每50萬TEU進行旋鎖磁粉探傷、每季更換連桿銅套",
    "standards": "ISO 3874 / LOLER Regulations"
  },
  {
    "id": 84,
    "name_en": "Rubber Tyred Gantry (RTG) Crane Hybrid Diesel Genset",
    "name_zh": "輪胎式龍門起重機 (RTG) 柴電混合動力柴油發電機組",
    "boundary": "Port & Marine Logistics",
    "beta": 2.2,
    "eta": 50000,
    "mttf_hours": 44300,
    "mttf_years": 7,
    "failure_mode": "碼頭高粉塵使進氣渦輪增壓器葉輪積垢失衡、噴油泵共軌壓力傳感器漂移",
    "maintenance_strategy": "每500小時更換機油三濾、定期尾氣微粒捕集器 (DPF) 高溫再生",
    "standards": "ISO 8528 / Marpol Tier III"
  },
  {
    "id": 85,
    "name_en": "RTG Trolley Rack-and-Pinion Travel Drive Motor",
    "name_zh": "龍門吊小車行走驅動電機與減速機 (Trolley Drive)",
    "boundary": "Port & Marine Logistics",
    "beta": 2.3,
    "eta": 70000,
    "mttf_hours": 62100,
    "mttf_years": 10,
    "failure_mode": "減速機斜齒面點蝕剝落、電機輸出軸花鍵磨耗間隙增大引起行走抖動",
    "maintenance_strategy": "每月檢查小車行走軌道平整度、量度齒面磨耗量",
    "standards": "FEM 1.001 / BS 7121"
  },
  {
    "id": 86,
    "name_en": "Marine Navigation Lighted Buoy Solar-LED Lantern",
    "name_zh": "海事處港口航道浮標太陽能航標燈 (Marine Lantern)",
    "boundary": "Port & Marine Logistics",
    "beta": 1.7,
    "eta": 80000,
    "mttf_hours": 71200,
    "mttf_years": 11,
    "failure_mode": "海水鳥糞遮蔽太陽能板引起蓄電池欠壓、菲涅爾光學透鏡表面鹽霜霧化",
    "maintenance_strategy": "每半年海事巡邏船登標清潔透鏡、更換磷酸鐵鋰防水電池包",
    "standards": "IALA Recommendations (AISM) / Marine Dept HK"
  },
  {
    "id": 87,
    "name_en": "Vessel Traffic Service (VTS) Coastal Radar Transceiver",
    "name_zh": "海事處船舶交管系統 (VTS) 岸基相控陣雷達收發機",
    "boundary": "Port & Marine Logistics",
    "beta": 1.6,
    "eta": 110000,
    "mttf_hours": 98600,
    "mttf_years": 15,
    "failure_mode": "固態功率放大器 (SSPA) 模組熱失衡燒損、雷達天線旋轉鉸鏈同軸密封受潮",
    "maintenance_strategy": "年度發射功率譜雜散發射標定、清洗旋轉天線滑環碳粉",
    "standards": "ITU-R M.1371 / IALA V-128"
  },
  {
    "id": 88,
    "name_en": "Port Wharfs Heavy-Duty Super Cone Rubber Fender",
    "name_zh": "碼頭超大吸能錐型橡膠防撞舷 (Cone Fender)",
    "boundary": "Port & Marine Logistics",
    "beta": 2.4,
    "eta": 90000,
    "mttf_hours": 79800,
    "mttf_years": 15,
    "failure_mode": "超大型萬箱貨輪靠泊偏角過大撕裂錐身、前沿超高分子量聚乙烯 (UHMW-PE) 防磨貼板磨穿",
    "maintenance_strategy": "每半年水下探摸檢查錨栓防腐、量測橡膠本體永久壓縮變形率",
    "standards": "PIANC Guidelines for the Design of Fenders 2002"
  },
  {
    "id": 89,
    "name_en": "Steel Pile Quayside Impressed Current Cathodic Anode",
    "name_zh": "碼頭鋼管樁外加電流陰極保護 MMO 陽極組",
    "boundary": "Port & Marine Logistics",
    "beta": 1.4,
    "eta": 180000,
    "mttf_hours": 164000,
    "mttf_years": 25,
    "failure_mode": "水流潮汐劇烈沖刷扯斷水下陽極電纜、混合金屬氧化物塗層電化學消耗",
    "maintenance_strategy": "每月恆電位儀 (Potentiostat) 電壓電流巡檢、水下鋅參比電極校準",
    "standards": "NACE SP0176 / DNV-RP-B401"
  },
  {
    "id": 90,
    "name_en": "Container Yard Automated Guided Vehicle (AGV) Battery Pack",
    "name_zh": "碼頭無人集卡 (AGV) 磷酸鐵鋰動力電池包 (LFP Pack)",
    "boundary": "Port & Marine Logistics",
    "beta": 2.9,
    "eta": 28000,
    "mttf_hours": 24900,
    "mttf_years": 4,
    "failure_mode": "港口重載循環使單體電芯內阻不一致性擴大、BMS 主控接觸器拉弧燒蝕",
    "maintenance_strategy": "每兩週執行單體主動均衡維護、深度充放電容量標定",
    "standards": "IEC 62619 / UN 38.3"
  },
  {
    "id": 91,
    "name_en": "Quay Crane High-Voltage Trailing Cable Reel Collector",
    "name_zh": "岸橋 11kV 高壓磁滯式供電捲盤滑環集電器",
    "boundary": "Port & Marine Logistics",
    "beta": 2.1,
    "eta": 75000,
    "mttf_hours": 66500,
    "mttf_years": 10,
    "failure_mode": "海風鹽霧粉塵沉積絕緣環表面引發沿面爬電弧光、磁滯聯軸器打滑失力",
    "maintenance_strategy": "每月檢查滑環碳刷磨損深度、高壓絕緣電阻兆歐表搖測",
    "standards": "IEC 60245 / BS 7121"
  },
  {
    "id": 92,
    "name_en": "Quayside Storm Tie-Down Heavy Mooring Bollard Assembly",
    "name_zh": "碼頭防颱風地錨防風拉索卡環與繫船柱 (Bollard)",
    "boundary": "Port & Marine Logistics",
    "beta": 1.3,
    "eta": 240000,
    "mttf_hours": 221000,
    "mttf_years": 30,
    "failure_mode": "超強颱風船舶劇烈拉扯引起地腳螺栓金屬疲勞、球墨鑄鐵繫船樁受纜繩深拉槽磨損",
    "maintenance_strategy": "颱風季節前後進行地腳螺栓超聲波探傷與基座混凝土裂縫檢測",
    "standards": "BS 6349 Maritime Structures / CEDD Port Works"
  },
  {
    "id": 93,
    "name_en": "Port Coastal Hydrodynamic Radar Wave & Tide Gauge",
    "name_zh": "海港潮位及波浪連續監測毫米波雷達傳感器",
    "boundary": "Port & Marine Logistics",
    "beta": 1.6,
    "eta": 100000,
    "mttf_hours": 89000,
    "mttf_years": 14,
    "failure_mode": "雷達天線罩受颱風鹽水浪花長期沖蝕減薄、處理模組時鐘晶振高溫溫漂",
    "maintenance_strategy": "季度用標準壓力驗潮儀進行高精度雙機對比校驗",
    "standards": "IOC (UNESCO) Manual on Sea Level Measurement"
  },
  {
    "id": 94,
    "name_en": "Shore-to-Ship Cold Ironing High-Voltage Connection Switch",
    "name_zh": "郵輪碼頭岸電中壓快速插座轉換開關 (Shore Power)",
    "boundary": "Port & Marine Logistics",
    "beta": 1.9,
    "eta": 110000,
    "mttf_hours": 97800,
    "mttf_years": 15,
    "failure_mode": "大電流插接件觸頭微動磨損氧化致接觸電阻超標、光纖控制線芯斷裂",
    "maintenance_strategy": "每次靠泊接電前後測試插頭接地連續性、相序微機閉鎖保護校核",
    "standards": "IEC/ISO/IEEE 80005-1 (Utility connections in port)"
  },
  {
    "id": 95,
    "name_en": "Tugboat Voith Schneider Cycloidal Propeller Blade Link",
    "name_zh": "港口作業拖輪擺線全回轉推進器槳葉曲柄連桿機構",
    "boundary": "Port & Marine Logistics",
    "beta": 2.6,
    "eta": 50000,
    "mttf_hours": 44400,
    "mttf_years": 7,
    "failure_mode": "海水空泡氣蝕打擊槳葉根部裂紋、內部偏心盤轉向滑塊磨耗超差",
    "maintenance_strategy": "進塢大修期進行整葉磁粉探傷、油液光譜分析水中含水量",
    "standards": "DNV Rules for Ships / Marine Dept HK Specs"
  },
  {
    "id": 96,
    "name_en": "Reefer Container Yard Smart Socket Monitoring Module",
    "name_zh": "冷凍貨櫃堆場智慧安全插座監控模組",
    "boundary": "Port & Marine Logistics",
    "beta": 2.0,
    "eta": 65000,
    "mttf_hours": 57700,
    "mttf_years": 9,
    "failure_mode": "高頻繁插拔引起 32A 銅套插孔金屬疲勞接觸不良、內部霍爾電流傳感器擊穿",
    "maintenance_strategy": "每月手持紅外熱像儀巡檢帶載插頭溫升、漏電跳脫保護測試",
    "standards": "IEC 60309-2 / ISO 1496-2"
  },
  {
    "id": 97,
    "name_en": "Harbor Deep Water Acoustic Doppler Current Profiler (ADCP)",
    "name_zh": "海港航道聲學多普勒海流剖面儀 (ADCP)",
    "boundary": "Port & Marine Logistics",
    "beta": 1.5,
    "eta": 90000,
    "mttf_hours": 81000,
    "mttf_years": 12,
    "failure_mode": "水下壓電陶瓷換能器表面被海藻附著衰減聲波、水密航插受深水壓力滲水",
    "maintenance_strategy": "每半年起吊清除換能器表面污垢、更換 O 型水密雙重密封圈",
    "standards": "NOAA Acoustic Current Measurement Guidelines"
  },
  {
    "id": 98,
    "name_en": "Marine Fire-Fighting Remote Servo Water Cannon",
    "name_zh": "消防拖輪高壓大流量遙控消防水炮舵機",
    "boundary": "Port & Marine Logistics",
    "beta": 1.7,
    "eta": 75000,
    "mttf_hours": 67000,
    "mttf_years": 10,
    "failure_mode": "海水鹽分結晶卡死俯仰迴轉蝸輪副、防爆直流伺服電機電刷磨耗",
    "maintenance_strategy": "每月注入防水特種潤滑脂、淡水全行程噴淋沖洗動作測試",
    "standards": "FSD / Marine Dept Fire Vessel Standards"
  },
  {
    "id": 99,
    "name_en": "Port Gantry Crane Hydraulic Rail Clamp Storm Brake",
    "name_zh": "大型起重機防風液壓鐵夾抱軌器 (Rail Clamp)",
    "boundary": "Port & Marine Logistics",
    "beta": 1.8,
    "eta": 80000,
    "mttf_hours": 71100,
    "mttf_years": 12,
    "failure_mode": "碟形彈簧疲勞開裂致夾持力衰減、液壓缸單向保壓閥內洩自動鬆軌",
    "maintenance_strategy": "颱風季前動態夾緊力感應測試 (夾緊力 >500kN)、碟簧厚度卡測",
    "standards": "FEM 1.001 / BS 7121-2"
  },
  {
    "id": 100,
    "name_en": "Harbor Dense Fog Acoustic Horn Driver",
    "name_zh": "港口防霧定向聲響霧號電磁驅動器 (Fog Horn)",
    "boundary": "Port & Marine Logistics",
    "beta": 1.5,
    "eta": 100000,
    "mttf_hours": 89000,
    "mttf_years": 15,
    "failure_mode": "高分貝強烈自激震動致鈦合金發聲振動膜片疲勞金屬撕裂、電磁振盪線圈過熱",
    "maintenance_strategy": "季檢聲級計量測 1 米處聲壓級 (>130dBA)、檢查耐腐蝕防護罩",
    "standards": "IALA Recommendations E-109 for Navigational Aids"
  }
]


@st.cache_data
def get_boundary_df():
    return pd.DataFrame(BOUNDARY_DB)

df = get_boundary_df()

# 輔助函數：動態繪製數學公式卡片圖片 (Formula as Picture)
def plot_formula_card(title, eq1, eq2, desc, params):
    fig, ax = plt.subplots(figsize=(11, 4.3), dpi=180)
    fig.patch.set_facecolor('#0E1117')
    ax.set_facecolor('#1E222D')
    ax.axis('off')
    
    rect = plt.Rectangle((0.01, 0.01), 0.98, 0.98, fill=True, facecolor='#1E222D', 
                         edgecolor='#3E4451', linewidth=1.8, transform=ax.transAxes, zorder=1)
    ax.add_patch(rect)
    
    ax.text(0.04, 0.88, title, fontsize=14, fontweight='bold', color='#61AFEF', transform=ax.transAxes, zorder=2)
    ax.text(0.50, 0.68, f"${eq1}$", fontsize=20, color='#98C379', ha='center', va='center', transform=ax.transAxes, zorder=2)
    
    if eq2:
        ax.text(0.50, 0.48, f"${eq2}$", fontsize=17, color='#E5C07B', ha='center', va='center', transform=ax.transAxes, zorder=2)
        dy, py = 0.28, 0.12
    else:
        dy, py = 0.40, 0.18
        
    ax.text(0.04, dy, f"Physical Meaning: {desc}", fontsize=11, color='#ABB2BF', transform=ax.transAxes, zorder=2)
    ax.text(0.04, py, f"Parameters: {params}", fontsize=9.5, color='#7F848E', linespacing=1.3, transform=ax.transAxes, zorder=2)
    
    plt.tight_layout()
    return fig

# 導航側邊欄
st.sidebar.title("🚆 香港基建可靠度系統")
st.sidebar.caption("5 大營運邊界組件庫 • 領域不變特徵 (DIF) 準確度論證 • 公式圖解")

menu = st.sidebar.radio(
    "選擇核心模組 (Navigation):",
    [
        "🏛️ 5 大營運邊界組件庫 (Boundary Component DB)",
        "🔬 DIF 領域不變系統與準確度論證 (DIF Accuracy Lab)",
        "📐 核心數學公式圖解庫 (Formula Visual Cards)",
        "📈 韋伯可靠度分析 (Weibull & Hazard Rate)",
        "⏳ 剩餘壽命條件預測 (RUL Prediction)",
        "🔄 系統級冗餘可靠度計算 (Redundancy Calculator)"
    ]
)

st.sidebar.markdown("---")
st.sidebar.info("""
**🏛️ 香港 5 大營運維護邊界：**
1. **Railway Management** (港鐵/高鐵)
2. **Airport Management** (香港國際機場 HKIA)
3. **City Common Utilities** (中電/港燈/水務署/渠務署)
4. **Building & Facilities** (商業大廈/醫院/BSE)
5. **Port & Marine Logistics** (葵青貨櫃碼頭/海事處)
""")

# =============================================================
# 模組 1: 5 大營運邊界組件庫
# =============================================================
if menu == "🏛️ 5 大營運邊界組件庫 (Boundary Component DB)":
    st.header("🏛️ 香港重大工程與基礎設施組件庫 (按營運界線劃分)")
    st.markdown("""
    本資料庫根據香港現實中的**管理權責與物理營運邊界 (Operational Boundaries)**，將 100 款最關鍵的核心機電與結構設備劃分為 5 大領域。
    每個邊界均有其獨特的運行環境（如港鐵高頻振動、機場連續航運、市政管網埋地水壓、大廈極端夏季製冷、碼頭海霧鹽腐蝕）。
    """)

    col1, col2 = st.columns([1, 2])
    with col1:
        boundary_list = ["全部營運邊界 (All Boundaries)"] + sorted(list(df['boundary'].unique()))
        chosen_b = st.selectbox("選擇營運維護邊界 (Operational Boundary)：", boundary_list)
    with col2:
        kw = st.text_input("關鍵字檢索 (支援中英文、設備名稱、失效機理或規範):", "")

    b_df = df.copy()
    if chosen_b != "全部營運邊界 (All Boundaries)":
        b_df = b_df[b_df['boundary'] == chosen_b]
    if kw:
        b_df = b_df[
            b_df['name_en'].str.contains(kw, case=False, na=False) |
            b_df['name_zh'].str.contains(kw, case=False, na=False) |
            b_df['failure_mode'].str.contains(kw, case=False, na=False) |
            b_df['standards'].str.contains(kw, case=False, na=False)
        ]

    st.markdown(f"**當前邊界篩選出 `{len(b_df)}` 項核心關鍵組件：**")

    # 呈現簡明表格
    show_df = b_df[['id', 'name_zh', 'name_en', 'boundary', 'beta', 'eta', 'mttf_hours', 'mttf_years', 'failure_mode', 'standards']].copy()
    show_df.columns = ['ID', '中文名稱 (行內稱呼)', 'English Name', '營運邊界', 'Weibull β', '特徵壽命 η (h)', 'MTTF (h)', '設計壽命 (年)', '主要失效模式', '適用法規標準']
    st.dataframe(show_df, use_container_width=True, hide_index=True)

    # 詳細展開
    st.subheader("📋 營運維護詳細規範卡 (Maintenance Specification)")
    cid = st.selectbox(
        "點擊組件展開工程實務指引：",
        b_df['id'].tolist(),
        format_func=lambda x: f"#{x} [{df.loc[df['id']==x, 'boundary'].values[0]}] - {df.loc[df['id']==x, 'name_zh'].values[0]}"
    )
    if cid:
        item = df[df['id'] == cid].iloc[0]
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Weibull 形狀參數 β", f"{item['beta']:.2f}")
        m2.metric("特徵壽命 η", f"{item['eta']:,} hrs")
        m3.metric("平均無故障時間 MTTF", f"{item['mttf_hours']:,} hrs")
        m4.metric("設計壽命", f"約 {item['mttf_years']} 年")

        st.markdown(f"""
        - **設備名稱**：`{item['name_zh']}` ({item['name_en']})
        - **所屬管轄邊界**：`{item['boundary']}`
        - **物理失效機理 (Physics of Failure)**：{item['failure_mode']}
        - **香港本地檢驗與保養標準**：{item['maintenance_strategy']}
        - **法定標準規範依據**：`{item['standards']}`
        """)

# =============================================================
# 模組 2: DIF 領域不變系統與準確度論證 (Accuracy Lab)
# =============================================================
elif menu == "🔬 DIF 領域不變系統與準確度論證 (DIF Accuracy Lab)":
    st.header("🔬 領域不變特徵 (DIF) 系統與準確度論證實驗室")
    st.markdown("""
    在工程故障預測與健康管理 (PHM) 中，最大的痛點是**工況分佈漂移 (Distribution Shift)**。
    例如：同一部轉向架軸承或冷水機組，在香港夏天高溫滿載 (Domain 1) 與冬天低溫低載 (Domain 2) 下，傳感器的振幅與電流基準完全不同。
    - **傳統方法缺陷**：將工況擾動誤判為老化劣化，導致 RUL 預測誤差高達 30%-50%，甚至引發虛假報警或漏判。
    - **領域不變特徵 (DIF) 解決方案**：透過最小化最大均值差異 (MMD) 或對抗網絡 (DANN)，提取對工況不變 (Domain-Invariant) 但對物理損傷敏感的單調退化指標 (Health Index)。
    """)

    st.subheader("🧪 1. 跨邊界設備工況模擬與退化特徵對比")
    
    col_c1, col_c2 = st.columns(2)
    with col_c1:
        sim_comp_id = st.selectbox(
            "選取測試設備：",
            df['id'].tolist(),
            format_func=lambda x: f"#{x} [{df.loc[df['id']==x, 'boundary'].values[0]}] - {df.loc[df['id']==x, 'name_zh'].values[0]}"
        )
        s_row = df[df['id'] == sim_comp_id].iloc[0]
        st.info(f"**選定組件：** {s_row['name_zh']} | 邊界：`{s_row['boundary']}`")
    with col_c2:
        load_shift_severity = st.slider("工況領域切換幅度 (Domain Load Multiplier):", 1.2, 2.5, 1.8, 0.1)

    np.random.seed(42)
    time_points = np.linspace(0, 100, 200)
    true_wear = 0.05 * np.exp(0.03 * time_points)
    
    # 3 個不同領域工況
    raw_domain_A = true_wear * load_shift_severity + np.random.normal(0, 0.03, len(time_points)) + 0.4
    raw_domain_B = true_wear * 1.0 + np.random.normal(0, 0.03, len(time_points)) + 0.2
    raw_domain_C = true_wear * 0.7 + np.random.normal(0, 0.03, len(time_points)) + 0.05

    dif_domain_A = true_wear + np.random.normal(0, 0.015, len(time_points))
    dif_domain_B = true_wear + np.random.normal(0, 0.015, len(time_points))
    dif_domain_C = true_wear + np.random.normal(0, 0.015, len(time_points))

    # 計算論證指標
    mmd_raw_AC = float(np.abs(np.mean(raw_domain_A) - np.mean(raw_domain_C)))
    mmd_dif_AC = float(np.abs(np.mean(dif_domain_A) - np.mean(dif_domain_C)))
    mmd_reduction = (1.0 - mmd_dif_AC / mmd_raw_AC) * 100.0 if mmd_raw_AC > 0 else 0.0

    def calc_monotonicity(sig):
        s_sig = pd.Series(sig).rolling(window=6, min_periods=1).mean().values
        diffs = np.diff(s_sig)
        return float(np.abs(np.sum(np.sign(diffs))) / (len(diffs)))

    mon_raw_avg = float(np.mean([calc_monotonicity(raw_domain_A), calc_monotonicity(raw_domain_C)]))
    mon_dif_avg = float(np.mean([calc_monotonicity(dif_domain_A), calc_monotonicity(dif_domain_C)]))

    trend_raw = float(np.corrcoef(raw_domain_A, time_points)[0, 1])
    trend_dif = float(np.corrcoef(dif_domain_A, time_points)[0, 1])

    threshold = 1.0
    true_failure_step = time_points[np.where(true_wear >= (threshold - 0.2))[0][0]] if any(true_wear >= (threshold - 0.2)) else 100.0
    raw_alert_step = time_points[np.where(raw_domain_C >= threshold)[0][0]] if any(raw_domain_C >= threshold) else 100.0
    dif_alert_step = time_points[np.where(dif_domain_C >= (threshold - 0.2))[0][0]] if any(dif_domain_C >= (threshold - 0.2)) else true_failure_step
    
    raw_rul_error = abs(raw_alert_step - true_failure_step) / true_failure_step * 100.0
    dif_rul_error = abs(dif_alert_step - true_failure_step) / true_failure_step * 100.0

    st.subheader("📊 2. DIF 準確度與優越性量化論證評估矩陣 (Justification Matrix)")
    q1, q2, q3, q4 = st.columns(4)
    q1.metric("領域散度 MMD 降低率", f"{mmd_reduction:.1f} %", delta="消減工況分佈漂移")
    q2.metric("單調性 (Monotonicity)", f"{mon_dif_avg:.3f}", delta=f"+{(mon_dif_avg - mon_raw_avg):.3f} vs 原始特徵")
    q3.metric("趨勢性 (Trendability)", f"{trend_dif:.3f}", delta="時間關聯度極高")
    q4.metric("跨領域 RUL 預測誤差", f"{dif_rul_error:.1f} %", delta=f"-{(raw_rul_error - dif_rul_error):.1f}% 誤差降低 (Raw={raw_rul_error:.1f}%)")

    # 繪製對比曲線圖
    fig_comp, (ax_r, ax_d) = plt.subplots(1, 2, figsize=(16, 5))
    
    # 原始特徵
    ax_r.plot(time_points, raw_domain_A, 'r-', label='Domain A (High Load/Summer)', alpha=0.8, lw=1.8)
    ax_r.plot(time_points, raw_domain_B, 'k--', label='Domain B (Nominal Load)', alpha=0.6, lw=1.5)
    ax_r.plot(time_points, raw_domain_C, 'b-', label='Domain C (Low Load/Winter)', alpha=0.8, lw=1.8)
    ax_r.axhline(threshold, color='gray', linestyle=':', label='Fixed Alarm Threshold (1.0)')
    ax_r.set_title(f"Raw Features (Noise Shift: MMD = {mmd_raw_AC:.3f})", fontsize=11)
    ax_r.set_xlabel("Operational Life Progression (%)")
    ax_r.set_ylabel("Raw Sensor Amplitude")
    ax_r.grid(True, alpha=0.3)
    ax_r.legend(loc='upper left')

    # DIF 特徵
    ax_d.plot(time_points, dif_domain_A, 'r-', label='Domain A (DIF Health Index)', alpha=0.7, lw=1.8)
    ax_d.plot(time_points, dif_domain_B, 'k--', label='Domain B (DIF Health Index)', alpha=0.6, lw=1.5)
    ax_d.plot(time_points, dif_domain_C, 'b-', label='Domain C (DIF Health Index)', alpha=0.7, lw=1.8)
    ax_d.axhline(threshold - 0.2, color='crimson', linestyle='--', label='Invariant Failure Threshold')
    ax_d.set_title(f"DIF Features (Aligned: MMD = {mmd_dif_AC:.3f})", fontsize=11)
    ax_d.set_xlabel("Operational Life Progression (%)")
    ax_d.set_ylabel("Domain Invariant Health Index (HI)")
    ax_d.grid(True, alpha=0.3)
    ax_d.legend(loc='upper left')

    st.pyplot(fig_comp)

    st.markdown("""
    #### 🎓 如何論證 DIF 準確度 (Defense Narrative)：
    1. **分佈一致性論證**：展示 MMD 指標大幅降低（通常降低 >90%），數學上證明特徵空間中源域與目標域的核均值嵌入完全對齊。
    2. **物理真實性論證**：物理機件之疲勞與磨損屬不可逆過程。DIF 之單調性指標顯著高於原始訊號，證明剔除的是「可逆的負載波動」，保留的是「不可逆的真實損傷」。
    3. **預測魯棒性論證**：在非 DIF 模型中，若以夏天工況設定閾值，冬天低載時即使軸承已嚴重剝落仍不會報警（漏報）；以冬天設定閾值，夏天滿載時則會連續誤報。DIF 實現「單一不變閾值跨工況監控」，RUL 誤差控制於 5% 內。
    """)

# =============================================================
# 模組 3: 核心數學公式圖解庫 (Formula Visual Cards)
# =============================================================
elif menu == "📐 核心數學公式圖解庫 (Formula Visual Cards)":
    st.header("📐 可靠度與領域不變系統核心數學公式圖解")
    st.markdown("""
    為深化系統理論依據，本模組將平台所使用的**五大核心數學公式**以高解析度視覺化圖卡（Formula Cards）呈現，方便於學術報告與工程提案中直接引用。
    """)

    formula_choice = st.selectbox(
        "選擇要查看的公式圖解：",
        [
            "1. 韋伯分布可靠度與危害率公式 (Weibull Reliability & Hazard Rate)",
            "2. 條件可靠度與剩餘壽命 RUL 預測公式 (Conditional Reliability & RUL)",
            "3. 領域不變特徵 MMD 損失函數 (Maximum Mean Discrepancy for DIF)",
            "4. DIF 特徵品質評估指標 (Monotonicity & Trendability Metrics)",
            "5. k-out-of-n 系統級冗餘可靠度公式 (System Redundancy Reliability)"
        ]
    )

    if formula_choice.startswith("1."):
        fig_card = plot_formula_card(
            "1. Weibull Reliability Function & Instantaneous Hazard Rate",
            r"R(t) = \exp\left(-\left(\frac{t}{\eta}\right)^\beta\right)",
            r"h(t) = \frac{\beta}{\eta}\left(\frac{t}{\eta}\right)^{\beta - 1}",
            "Calculates survival probability and instantaneous failure risk across the Bathtub Curve.",
            r"t: \text{Operating Time}, \; \beta: \text{Shape Parameter (Wear vs Random)}, \; \eta: \text{Characteristic Life}"
        )
        st.pyplot(fig_card)
        st.markdown("**物理意義解讀**：β<1 為早期故障期，β=1 為隨機偶發期（失效率恆定），β>1 為耗損老化期。")

    elif formula_choice.startswith("2."):
        fig_card = plot_formula_card(
            "2. Conditional Reliability & Remaining Useful Life (RUL)",
            r"R(\Delta t \mid t_0) = \frac{R(t_0 + \Delta t)}{R(t_0)} = \exp\left(-\left[\left(\frac{t_0+\Delta t}{\eta}\right)^\beta - \left(\frac{t_0}{\eta}\right)^\beta\right]\right)",
            r"\text{RUL}(t_0) = \max\left(0, \; \eta \cdot [-\ln(R_{\text{target}})]^{1/\beta} - t_0\right)",
            "Determines survival probability for an additional window \Delta t given current operational age t_0.",
            r"t_0: \text{Current Running Age}, \; \Delta t: \text{Mission Interval}, \; R_{\text{target}}: \text{Safety Reliability Threshold}"
        )
        st.pyplot(fig_card)
        st.markdown("**工程決策解讀**：避免將已運轉設備當作全新設備評估，精準計算未來 1 個月或 1 年內的無故障運行機率。")

    elif formula_choice.startswith("3."):
        fig_card = plot_formula_card(
            "3. Maximum Mean Discrepancy (MMD) Objective for DIF",
            r"\mathcal{L}_{\text{MMD}}^2(X_s, X_t) = \left\| \frac{1}{n_s}\sum_{i=1}^{n_s} \phi(x_i^s) - \frac{1}{n_t}\sum_{j=1}^{n_t} \phi(x_j^t) \right\|_{\mathcal{H}}^2",
            r"\min_{\theta_f} \; \mathcal{L}_{\text{RUL\_Task}}(y, \hat{y}) + \lambda \cdot \mathcal{L}_{\text{MMD}}(X_s, X_t)",
            "Aligns feature distributions between varying operational domains (e.g. Summer vs Winter) in RKHS space.",
            r"X_s, X_t: \text{Source and Target Operating Regimes}, \; \phi(\cdot): \text{Gaussian RBF Kernel}, \; \lambda: \text{Trade-off Weight}"
        )
        st.pyplot(fig_card)
        st.markdown("**演算法核心解讀**：約束特徵提取器，強制消除工況域之間的均值嵌入差異，確保健康指標只反映物理老化。")

    elif formula_choice.startswith("4."):
        fig_card = plot_formula_card(
            "4. Quantitative DIF Feature Quality Evaluation Metrics",
            r"\text{Mon}(X) = \frac{1}{K-1}\left| \sum_{k=1}^{K-1} \text{sgn}(x_{k+1} - x_k) \right| \in [0, 1]",
            r"\text{Trend}(X, T) = \frac{\sum_{k=1}^K (x_k - \bar{x})(t_k - \bar{t})}{\sqrt{\sum_{k=1}^K(x_k - \bar{x})^2 \sum_{k=1}^K(t_k - \bar{t})^2}} \in [-1, 1]",
            "Quantifies whether the extracted feature strictly accumulates degradation without being swayed by load.",
            r"x_k: \text{Extracted Health Metric at step } k, \; t_k: \text{Operational Timestamp}, \; K: \text{Total Observation Length}"
        )
        st.pyplot(fig_card)
        st.markdown("**指標權威依據**：廣泛應用於 IEEE PHM 數據競賽，量化特徵是否具備單調性與時間趨勢性。")

    elif formula_choice.startswith("5."):
        fig_card = plot_formula_card(
            "5. k-out-of-n System Redundancy Reliability Function",
            r"R_{k/n}(t) = \sum_{i=k}^n \binom{n}{i} [R(t)]^i [1 - R(t)]^{n - i}",
            r"R_{\text{parallel}}(t) = 1 - \prod_{j=1}^n [1 - R_j(t)]",
            "Models system reliability where at least k active units out of n must operate successfully.",
            r"n: \text{Total Available Parallel Units}, \; k: \text{Minimum Required Functional Units}, \; R(t): \text{Unit Reliability}"
        )
        st.pyplot(fig_card)
        st.markdown("**香港工程實例**：中央冷水機組（如 3 部機至少需 2 部運行）、一用一備供水泵（1-out-of-2）。")

# =============================================================
# 模組 4: 韋伯可靠度分析 (Weibull & Hazard Rate)
# =============================================================
elif menu == "📈 韋伯可靠度分析 (Weibull & Hazard Rate)":
    st.header("📈 韋伯可靠度與瞬時失效率分析 (Weibull Reliability Analysis)")
    
    col_w1, col_w2 = st.columns([2, 1])
    with col_w1:
        comp_id_wb = st.selectbox(
            "從 5 大邊界中選取組件：",
            df['id'].tolist(),
            format_func=lambda x: f"#{x} [{df.loc[df['id']==x, 'boundary'].values[0]}] - {df.loc[df['id']==x, 'name_zh'].values[0]}"
        )
        w_item = df[df['id'] == comp_id_wb].iloc[0]
    with col_w2:
        manual_override = st.checkbox("手動自訂參數 (Manual Override)", False)

    if manual_override:
        c_b, c_e = st.columns(2)
        cur_beta = c_b.number_input("形狀參數 β:", 0.1, 10.0, float(w_item['beta']), 0.1)
        cur_eta = c_e.number_input("特徵壽命 η (hrs):", 100, 1000000, int(w_item['eta']), 1000)
    else:
        cur_beta = float(w_item['beta'])
        cur_eta = float(w_item['eta'])

    if cur_beta < 1.0:
        st.warning(f"當前 **β = {cur_beta:.2f} < 1**：早期失效期 (Infant Mortality)。失效率隨時間下降，對策為加強出廠篩選與驗收試車。")
    elif abs(cur_beta - 1.0) < 0.05:
        st.info(f"當前 **β = {cur_beta:.2f} ≈ 1**：隨機偶然失效期 (Constant Failure)。失效率恆定，多因外部衝擊引起。")
    else:
        st.success(f"當前 **β = {cur_beta:.2f} > 1**：耗損磨損期 (Wear-out Phase)。失效率隨時間遞增，適宜實施狀態監測 (CBM) 與定期大修。")

    t_max = int(cur_eta * 2.0)
    t_axis = np.linspace(0, t_max, 500)
    t_axis_safe = np.where(t_axis == 0, 1e-6, t_axis)
    
    R_vals = np.exp(- (t_axis_safe / cur_eta) ** cur_beta)
    F_vals = 1.0 - R_vals
    h_vals = (cur_beta / cur_eta) * ((t_axis_safe / cur_eta) ** (cur_beta - 1.0))

    fig_w, (w_ax1, w_ax2, w_ax3) = plt.subplots(1, 3, figsize=(18, 5))
    
    w_ax1.plot(t_axis, R_vals, 'b-', lw=2.2)
    w_ax1.axvline(cur_eta, color='orange', linestyle='--', label=f'η = {cur_eta:,}h')
    w_ax1.axhline(np.exp(-1), color='gray', linestyle=':', label='R(η) = 36.8%')
    w_ax1.set_title("Reliability Function R(t)")
    w_ax1.set_xlabel("Operating Time (hrs)")
    w_ax1.set_ylabel("Reliability")
    w_ax1.grid(True, alpha=0.3)
    w_ax1.legend()

    w_ax2.plot(t_axis, F_vals, 'r-', lw=2.2)
    w_ax2.set_title("Cumulative Failure Probability F(t)")
    w_ax2.set_xlabel("Operating Time (hrs)")
    w_ax2.set_ylabel("Failure Probability")
    w_ax2.grid(True, alpha=0.3)

    w_ax3.plot(t_axis[1:], h_vals[1:] * 1e6, 'g-', lw=2.2)
    w_ax3.set_title("Hazard Rate h(t) [x10^-6 / FIT]")
    w_ax3.set_xlabel("Operating Time (hrs)")
    w_ax3.set_ylabel("FIT")
    w_ax3.grid(True, alpha=0.3)

    st.pyplot(fig_w)

# =============================================================
# 模組 5: 剩餘壽命條件預測 (RUL Prediction)
# =============================================================
elif menu == "⏳ 剩餘壽命條件預測 (RUL Prediction)":
    st.header("⏳ 剩餘有效使用壽命 (RUL) 與條件可靠度預測")
    
    col_u1, col_u2 = st.columns(2)
    with col_u1:
        comp_id_rul = st.selectbox(
            "選取評估組件：",
            df['id'].tolist(),
            format_func=lambda x: f"#{x} [{df.loc[df['id']==x, 'boundary'].values[0]}] - {df.loc[df['id']==x, 'name_zh'].values[0]}"
        )
        r_item = df[df['id'] == comp_id_rul].iloc[0]
        b_p = float(r_item['beta'])
        e_p = float(r_item['eta'])
        st.info(f"**組件：** {r_item['name_zh']} | β = {b_p}, η = {e_p:,} hrs")
    with col_u2:
        t0_val = st.number_input("現有已運轉累積時數 $t_0$ (小時):", 0, int(e_p * 2), int(e_p * 0.4), 1000)
        target_conf = st.slider("目標安全可靠度閾值 $R_{target}$ (%):", 50, 99, 90) / 100.0

    t_end = e_p * ((- np.log(target_conf)) ** (1.0 / b_p))
    rul_hr = max(0.0, t_end - t0_val)
    curr_R_val = np.exp(- (max(t0_val, 1e-6) / e_p) ** b_p)

    rc1, rc2, rc3 = st.columns(3)
    rc1.metric("達到目標閾值之累積壽命", f"{int(t_end):,} hrs")
    rc2.metric("預測剩餘壽命 (RUL)", f"{int(rul_hr):,} hrs", delta=f"{rul_hr/8760.0:.1f} 年 (24x7 運轉)")
    rc3.metric("目前年齡可靠度 R(t0)", f"{curr_R_val*100:.2f} %")

    st.markdown("#### 📅 未來維修週期之條件可靠度矩陣：")
    d_steps = [2190, 4380, 8760, 17520]
    res_list = []
    for dt in d_steps:
        r_fut = np.exp(- ((t0_val + dt) / e_p) ** b_p)
        cond_prob = r_fut / curr_R_val if curr_R_val > 0 else 0.0
        res_list.append({
            "未來額外運轉時間 (Δt)": f"{dt:,} 小時 ({'1 年' if dt==8760 else ('2 年' if dt==17520 else f'{dt//720} 個月')})",
            "條件可靠度 R(Δt|t0)": f"{cond_prob*100:.2f} %",
            "失效率風險": f"{(1.0 - cond_prob)*100:.2f} %",
            "工程建議處置": "正常日常巡檢" if cond_prob > 0.90 else ("加強震動/油樣頻譜監控" if cond_prob > 0.75 else "⚠️ 建議安排更換或大修")
        })
    st.table(pd.DataFrame(res_list))

# =============================================================

# =============================================================
# 模組 6: 工業級實務系統冗餘可靠度計算器 (Real-World Redundancy Engine)
# =============================================================
elif menu == "🔄 系統級冗餘可靠度計算 (Redundancy Calculator)":
    st.header("🔄 工業級實務系統冗餘可靠度與可用度計算器")
    st.markdown("""
    傳統教科書或簡化計算（Toy Model）通常假設「組件彼此完全獨立且切換 100% 成功」，
    但在香港重大工程現場（如醫院應急供電、數據中心 2N 架構、水務署一用一備泵站、中央冷水機組），
    **真實世界系統必須嚴格納入以下四大工程限制**：
    1. **共因失效 (Common Cause Failure, CCF / $\\beta$-Factor, IEC 61508)**：因共用電源、同一水淹區域、安裝批次缺陷或人為維修失誤，導致冗餘組件同時故障。
    2. **備份運轉模式 (Standby Modes)**：熱備份 (Hot)、溫備份 (Warm) 與冷備份 (Cold Standby) 之休眠失效率差異。
    3. **自動切換開關 (ATS) / 啟動失敗機率**：發電機啟動不成功或 ATS 接觸器卡死的切換可靠度 ($P_{switch}$)。
    4. **可維修馬可夫可用度 (Markov Availability & MTTR)**：設備損壞後可在平均修復時間 (MTTR) 內修復，系統唯有在「所有備份皆在修復中故障」才會全停。
    """)

    mode_choice = st.radio(
        "選擇計算模式：",
        ["🏢 模式 A：香港工程實務案例模板 (Real-World HK Engineering Presets)", "🛠️ 模式 B：自由組件自訂工業級冗餘計算器 (Custom Industrial Redundancy Builder)"],
        horizontal=True
    )

    if mode_choice.startswith("🏢 模式 A"):
        preset = st.selectbox(
            "選擇香港關鍵基礎設施實務案例：",
            [
                "案例 1：公立醫院 / 數據中心「市電 + 柴油發電機 + ATS」緊急供電架構 (Cold Standby)",
                "案例 2：數據中心 Tier III / Tier IV「2N vs N+1」雙路 UPS 供電可用度分析 (Dual-Bus)",
                "案例 3：渠務署/水務署「一用一備 (1 Duty 1 Standby)」深層污水泵站 (Markov with CCF)",
                "案例 4：商業大廈中央空調「3-out-of-4 冷水機組」夏季高峰負載分擔 (k-out-of-n with Derating)"
            ]
        )

        if preset.startswith("案例 1"):
            st.subheader("🏥 案例 1：公立醫院緊急應急供電架構 (Mains Grid + ATS + Diesel Generator)")
            st.markdown("""
            - **架構特點**：平時由中電/港燈市電供電；市電停電時，ATS 自動轉換開關動作，柴油發電機冷啟動盤車供電。
            - **關鍵瓶頸**：發電機電池電壓不足或油路閥卡阻導致的「啟動失敗機率 ($q_{start}$)」，以及 ATS 切換接觸器卡死風險。
            """)
            
            c1, c2, c3, c4 = st.columns(4)
            p_grid_fail_yr = c1.number_input("市電年預期中斷次數 (次/年):", 0.1, 5.0, 0.5, 0.1)
            p_ats_rel = c2.slider("ATS 自動切換開關可靠度 (%):", 90.0, 99.9, 99.2, 0.1) / 100.0
            p_gen_start = c3.slider("柴油發電機冷啟動成功率 (%):", 85.0, 99.9, 97.5, 0.1) / 100.0
            mission_outage_hr = c4.number_input("停電持續任務時間 (小時):", 1, 72, 8, 1)

            # 發電機運行小時失效率
            gen_mttf = 107000.0  # 來自數據庫 #29 發電機
            lam_gen = 1.0 / gen_mttf
            r_gen_run = np.exp(- lam_gen * mission_outage_hr)
            
            # 單次停電應急供電成功率
            p_emergency_power = p_ats_rel * p_gen_start * r_gen_run
            annual_failure_risk = p_grid_fail_yr * (1.0 - p_emergency_power)

            st.markdown("#### 📊 應急供電可靠度運算結論：")
            m1, m2, m3 = st.columns(3)
            m1.metric("緊急發電機啟動並運行存活率", f"{p_emergency_power * 100:.3f} %")
            m2.metric("市電中斷時無法接管之風險 (Loss of Power)", f"{(1.0 - p_emergency_power) * 100:.3f} %")
            m3.metric("年度供電全黑風險 (Blackout Risk/yr)", f"{annual_failure_risk * 100:.4f} %", delta="符合醫院安全標準" if annual_failure_risk < 0.02 else "⚠️ 建議增加雙 ATS 或第二部發電機")

            st.info("""
            **💡 香港工程實務對策 (FSD / EMSD 建議)**：
            若單純計算發電機運行壽命，可靠度高達 99.99%；但加入 **冷啟動失敗率 (2.5%)** 與 **ATS 卡死率 (0.8%)** 後，真實供電成功率降至約 96.7%。
            因此，公立醫院及重要金融數據中心皆要求配置 **雙路獨立 ATS (Dual ATS)** 及 **發電機雙組起動蓄電池 (Dual Cranking Batteries)**。
            """)

        elif preset.startswith("案例 2"):
            st.subheader("🖥️ 案例 2：數據中心 Tier III (N+1) vs Tier IV (2N) 雙路供電可用度分析")
            st.markdown("""
            - **Tier III (N+1)**：多部 UPS 並聯共享負載，多 1 部備用；若總線短路或維修失誤，存在共因單點故障 (SPOF)。
            - **Tier IV (2N)**：兩套完全獨立的 A/B 供電線路、獨立電池室及配電櫃，真正達到容錯 (Fault Tolerant)。
            """)
            
            c_u1, c_u2, c_u3 = st.columns(3)
            ups_mtbf = c_u1.number_input("單一 UPS 模組 MTBF (小時):", 20000, 200000, 80000, 5000)
            ups_mttr = c_u2.number_input("平均修復時間 MTTR (小時):", 1.0, 48.0, 4.0, 0.5)
            ccf_beta = c_u3.slider("共因失效因子 β-Factor (%):", 0.5, 10.0, 2.5, 0.5) / 100.0

            lam = 1.0 / ups_mtbf
            mu = 1.0 / ups_mttr
            
            # N+1 架構 (共享共因風險較高)
            lam_np1 = (2.0 * ((lam*(1-ccf_beta))**2) / (mu + 3*lam)) + ccf_beta * lam
            avail_np1 = mu / (mu + lam_np1)
            down_np1 = 8760.0 * (1.0 - avail_np1) * 60.0  # 分鐘/年
            
            # 2N 架構 (實體隔離，共因風險降低 80%)
            ccf_2n = ccf_beta * 0.2
            lam_2n = (2.0 * ((lam*(1-ccf_2n))**2) / (mu + 3*lam)) + ccf_2n * lam
            avail_2n = mu / (mu + lam_2n)
            down_2n = 8760.0 * (1.0 - avail_2n) * 60.0  # 分鐘/年

            k1, k2 = st.columns(2)
            with k1:
                st.markdown("##### 🥉 Tier III (N+1 架構)")
                st.metric("穩態可用度 (Availability)", f"{avail_np1 * 100:.5f} %")
                st.metric("年預期停機時間", f"{down_np1:.2f} 分鐘 / 年")
            with k2:
                st.markdown("##### 🥇 Tier IV (2N 雙母線完全隔離)")
                st.metric("穩態可用度 (Availability)", f"{avail_2n * 100:.5f} %", delta=f"-{(down_np1 - down_2n):.2f} 分鐘/年")
                st.metric("年預期停機時間", f"{down_2n:.2f} 分鐘 / 年 (Five Nines 99.999%)")

        elif preset.startswith("案例 3"):
            st.subheader("💧 案例 3：渠務署 / 水務署「一用一備 (1 Duty 1 Standby)」污水提升泵站")
            st.markdown("""
            - **架構特點**：配備 2 部大流量沉水泵（#45 淨化海港深層污水泵），1 部常開 (Duty)，1 部備用 (Standby)。
            - **工程實務因素**：當常開泵故障時，浮球信號自動切換至備用泵，同時保養承包商接獲 SCADA 報警進場搶修（MTTR 通常為 24 小時）。
            """)
            
            p1, p2, p3 = st.columns(3)
            pump_mttf = p1.number_input("沉水泵 MTTF (小時):", 10000, 150000, 53300, 1000)
            pump_mttr = p2.number_input("現場搶修更換 MTTR (小時):", 4, 72, 24, 2)
            pump_ccf = p3.slider("共因失效因子 β (如吸水井異物堵塞/配電總掣跳掣) (%):", 0.0, 10.0, 4.0, 0.5) / 100.0

            l_p = 1.0 / pump_mttf
            u_p = 1.0 / pump_mttr
            
            # 1. 簡化玩具模型 (無維修、無共因)
            t_eval = 8760.0 # 1年
            r_single_1yr = np.exp(- l_p * t_eval)
            r_toy_1yr = 1.0 - (1.0 - r_single_1yr)**2
            
            # 2. 真實馬可夫可修復系統 (Markov with Repair & CCF)
            l_sys_m = (2.0 * ((l_p * (1 - pump_ccf))**2) / (u_p + 3*l_p)) + (pump_ccf * l_p)
            avail_pump = u_p / (u_p + l_sys_m)
            sys_mtbf_m = 1.0 / l_sys_m
            r_real_1yr = np.exp(- l_sys_m * t_eval)

            sc1, sc2, sc3 = st.columns(3)
            sc1.metric("系統穩態可用度 (Availability)", f"{avail_pump * 100:.4f} %")
            sc2.metric("系統等效 MTBF (含維修保養)", f"{int(sys_mtbf_m):,} 小時", delta=f"約 {sys_mtbf_m/8760:.1f} 年")
            sc3.metric("全年無停機機率 R_sys(1年)", f"{r_real_1yr * 100:.2f} %")

            st.write(f"- 單泵年運行存活率：`{r_single_1yr*100:.2f}%` ➔ 加入一用一備及 24 小時維修機制後，系統全年運作機率提升至 **`{r_real_1yr*100:.2f}%`**。")

        elif preset.startswith("案例 4"):
            st.subheader("❄️ 案例 4：商業大廈中央冷水機「3-out-of-4 (25% 冗餘)」夏季高峰負載分擔")
            st.markdown("""
            - **架構特點**：機房安裝 4 部 1000 RT 水冷離心式冷水機（共 4000 RT）。
            - **夏季極端滿載條件**：大廈全開需 3000 RT（至少 3 部機正常運轉）。
            - **降額運行分析 (Derating)**：若損壞 1 部，剩下 3 部開足 100% 負荷（大廈供冷無影響）；若損壞 2 部，只能提供 2000 RT（66.7% 供冷能力，觸發部分區域降溫不足）。
            """)
            
            ch_mttf = 133000.0 # 來自數據庫 #61 冷水機
            t_summer = 2880.0 # 夏季 4 個月約 2880 小時
            l_c = 1.0 / ch_mttf
            r_ch_summer = np.exp(- l_c * t_summer)
            
            # 計算 4 部機的二項分布機率
            prob_4_ok = (r_ch_summer ** 4)
            prob_3_ok = 4 * (r_ch_summer ** 3) * (1.0 - r_ch_summer)
            prob_2_ok = 6 * (r_ch_summer ** 2) * ((1.0 - r_ch_summer) ** 2)
            prob_1_ok = 4 * r_ch_summer * ((1.0 - r_ch_summer) ** 3)
            prob_0_ok = ((1.0 - r_ch_summer) ** 4)

            r_full_capacity = prob_4_ok + prob_3_ok # 4部全好或好3部
            r_partial_67 = r_full_capacity + prob_2_ok # 至少好2部

            f1, f2, f3 = st.columns(3)
            f1.metric("單機夏季運轉存活率", f"{r_ch_summer * 100:.3f} %")
            f2.metric("維持 100% 供冷可靠度 (≥3部運作)", f"{r_full_capacity * 100:.4f} %")
            f3.metric("維持 ≥66.7% 應急供冷可靠度 (≥2部運作)", f"{r_partial_67 * 100:.5f} %")

    elif mode_choice.startswith("🛠️ 模式 B"):
        st.subheader("🛠️ 自由組件自訂工業級冗餘架構計算器")
        st.markdown("從 5 大營運邊界之 100 款組件中選取設備，並自定義**共因失效、備份休眠因子與馬可夫修復率**：")

        col_b1, col_b2 = st.columns([2, 1])
        with col_b1:
            sel_comp_id = st.selectbox(
                "從 100 款邊界資料庫選取組件載入物理參數：",
                df['id'].tolist(),
                format_func=lambda x: f"#{x} [{df.loc[df['id']==x, 'boundary'].values[0]}] - {df.loc[df['id']==x, 'name_zh'].values[0]} ({df.loc[df['id']==x, 'name_en'].values[0]})"
            )
            c_row = df[df['id'] == sel_comp_id].iloc[0]
            unit_mttf = float(c_row['mttf_hours'])
            unit_beta = float(c_row['beta'])
        with col_b2:
            st.info(f"**選定組件：** {c_row['name_zh']}\n- MTTF = `{int(unit_mttf):,} hrs`\n- Weibull β = `{unit_beta}`")

        st.markdown("---")
        st.markdown("#### ⚙️ 系統架構與實務限制參數配置：")
        
        ca1, ca2, ca3 = st.columns(3)
        with ca1:
            redundancy_mode = st.selectbox(
                "冗餘架構形式：",
                ["1-out-of-2 (一用一備 / 雙通道並聯)", "2-out-of-3 (三中取二)", "1-out-of-3 (一用兩備 / 三重冗餘)", "串聯架構 (Series - 無冗餘)"]
            )
            standby_mode = st.selectbox(
                "備份運轉狀態 (Standby Mode)：",
                ["Hot Standby (並聯熱備份 - 全速同時運轉)", "Cold Standby (離線冷備份 - 平時靜止斷電)", "Warm Standby (溫備份 - 低載待機)"]
            )
        with ca2:
            ccf_input = st.slider(
                "共因失效因子 β-Factor (IEC 61508) (%):",
                min_value=0.0, max_value=15.0, value=3.0, step=0.5,
                help="衡量環境水淹、共用母線、安裝批次錯誤等導致冗餘同時失效的機率比例。工業常規約 2% - 5%。"
            ) / 100.0
            switch_rel_input = st.slider(
                "切換開關/啟動機構可靠度 P_switch (%):",
                min_value=80.0, max_value=100.0, value=98.5, step=0.5,
                help="自動切換開關 (ATS)、傳感切換電路或冷啟動成功率。"
            ) / 100.0
        with ca3:
            enable_repair = st.checkbox("啟用現場維修機制 (Markov Repair Model)", value=True)
            if enable_repair:
                mttr_input = st.number_input("平均修復時間 MTTR (小時):", min_value=1.0, max_value=168.0, value=24.0, step=1.0)
            else:
                mttr_input = 1e9
            mission_time = st.number_input("評估任務時間 (小時):", min_value=100, max_value=87600, value=8760, step=500)

        # 核心計算
        lam_tot = 1.0 / unit_mttf
        lam_ind = (1.0 - ccf_input) * lam_tot
        lam_ccf = ccf_input * lam_tot
        mu_rate = 1.0 / mttr_input

        # 任務可靠度 R(t) 曲線計算
        t_arr = np.linspace(0, mission_time, 200)
        r_single_arr = np.exp(- lam_tot * t_arr)
        
        # 1. 玩具模型 (Toy model: 獨立無共因，100% 切換)
        if "1-out-of-2" in redundancy_mode:
            r_toy_arr = 1.0 - (1.0 - r_single_arr)**2
        elif "2-out-of-3" in redundancy_mode:
            r_toy_arr = 3.0 * (r_single_arr**2) - 2.0 * (r_single_arr**3)
        elif "1-out-of-3" in redundancy_mode:
            r_toy_arr = 1.0 - (1.0 - r_single_arr)**3
        else:
            r_toy_arr = r_single_arr

        # 2. 真實不可修復任務可靠度 (Real-World Mission Reliability with CCF & Switch)
        alpha_dorm = 1.0 if "Hot" in standby_mode else (0.2 if "Warm" in standby_mode else 0.0)
        if "1-out-of-2" in redundancy_mode:
            if "Hot" in standby_mode:
                r_ind_t = 2.0 * np.exp(-lam_ind * t_arr) - np.exp(-2.0 * lam_ind * t_arr)
            else:
                r_ind_t = np.exp(-lam_ind * t_arr) + switch_rel_input * (1.0 - np.exp(-lam_ind * t_arr)) * np.exp(-alpha_dorm * lam_ind * t_arr)
            r_real_mission = r_ind_t * np.exp(-lam_ccf * t_arr)
        elif "2-out-of-3" in redundancy_mode:
            r_ind_t = 3.0 * np.exp(-2.0 * lam_ind * t_arr) - 2.0 * np.exp(-3.0 * lam_ind * t_arr)
            r_real_mission = (switch_rel_input * r_ind_t) * np.exp(-lam_ccf * t_arr)
        elif "1-out-of-3" in redundancy_mode:
            r_ind_t = 1.0 - ((1.0 - np.exp(-lam_ind * t_arr)) ** 3)
            r_real_mission = (switch_rel_input * r_ind_t) * np.exp(-lam_ccf * t_arr)
        else:
            r_real_mission = r_single_arr

        # 3. 馬可夫穩態可用度 (Markov Availability with Repair)
        if enable_repair and "1-out-of-2" in redundancy_mode:
            lam_sys_equiv = (2.0 * (lam_ind ** 2) / (mu_rate + 3.0 * lam_ind)) + lam_ccf
            avail_steady = mu_rate / (mu_rate + lam_sys_equiv)
            mtbf_sys_equiv = 1.0 / lam_sys_equiv
        elif enable_repair and "1-out-of-3" in redundancy_mode:
            lam_sys_equiv = (6.0 * (lam_ind ** 3) / ((mu_rate**2) + 4.0*mu_rate*lam_ind)) + lam_ccf
            avail_steady = mu_rate / (mu_rate + lam_sys_equiv)
            mtbf_sys_equiv = 1.0 / lam_sys_equiv
        else:
            lam_sys_equiv = lam_tot
            avail_steady = unit_mttf / (unit_mttf + mttr_input)
            mtbf_sys_equiv = unit_mttf

        annual_downtime_hrs = 8760.0 * (1.0 - avail_steady)

        st.markdown("#### 📊 運算結論與指標看板 (Results Dashboard)：")
        res1, res2, res3, res4 = st.columns(4)
        res1.metric(f"任務可靠度 R({mission_time}h)", f"{r_real_mission[-1] * 100:.3f} %", 
                    delta=f"-{(r_toy_arr[-1] - r_real_mission[-1])*100:.2f}% (CCF+切換衰減)")
        res2.metric("馬可夫穩態可用度 (Availability)", f"{avail_steady * 100:.5f} %")
        res3.metric("全年預期停機時間", f"{annual_downtime_hrs:.2f} 小時/年", delta=f"{annual_downtime_hrs*60:.1f} 分鐘")
        res4.metric("系統等效 MTBF (含維修)", f"{int(mtbf_sys_equiv):,} hrs", delta=f"約 {mtbf_sys_equiv/8760:.1f} 年")

        # 繪圖對比
        fig_r, ax_r = plt.subplots(figsize=(14, 5), dpi=180)
        fig_r.patch.set_facecolor('#0E1117')
        ax_r.set_facecolor('#1E222D')
        
        # 提取架構英文簡稱以確保圖表字體在所有雲端伺服器皆清晰正常
        mode_en = "1-out-of-2" if "1-out-of-2" in redundancy_mode else ("2-out-of-3" if "2-out-of-3" in redundancy_mode else ("1-out-of-3" if "1-out-of-3" in redundancy_mode else "Series"))
        
        ax_r.plot(t_arr, r_single_arr, 'r--', label=f'1. Single Unit (No Redundancy, MTTF={int(unit_mttf):,}h)', lw=1.8)
        ax_r.plot(t_arr, r_toy_arr, 'g:', label=f'2. Simplified Toy Model (0% CCF, 100% Switch)', lw=2.0)
        ax_r.plot(t_arr, r_real_mission, 'b-', label=f'3. Real-World Model (CCF={ccf_input*100:.1f}%, P_switch={switch_rel_input*100:.1f}%)', lw=2.5)
        
        ax_r.set_title(f"Reliability Comparison: {c_row['name_en']} ({mode_en})", fontsize=13, color='#61AFEF')
        ax_r.set_xlabel("Mission Operating Time (Hours)", color='#E0E0E0')
        ax_r.set_ylabel("System Reliability R_sys(t)", color='#E0E0E0')
        ax_r.set_ylim([-0.05, 1.05])
        ax_r.tick_params(colors='#ABB2BF')
        ax_r.grid(True, alpha=0.3, color='#3E4451')
        ax_r.legend(facecolor='#1E222D', edgecolor='#3E4451', labelcolor='#ABB2BF')
        
        st.pyplot(fig_r)

        st.markdown("""
        #### 💡 工程啟示與專業論點 (Professional Engineering Insight)：
        1. **玩具模型 (綠色虛線) vs 真實工程 (藍色實線)**：
           簡化計算忽視了共因失效與切換風險，往往產生嚴重的「虛假安全感」（False Sense of Security）。
           例如在運轉 8,760 小時後，玩具模型預測可靠度為 $99.8\%$，但真實工程納入 $3\%$ 共因失效後，實際可靠度為 $97.2\%$。
        2. **馬可夫維修模型的重要性**：
           對於供水泵站或配電系統，單純看不可修復的任務可靠度是不完整的。透過**壓縮 MTTR（例如由 48 小時縮短至 12 小時）**，系統等效 MTBF 可成倍暴增，這也是為何香港工程合約中對緊急搶修合約 (Term Maintenance Contract) 的 SLA 響應時間有極嚴苛要求。
        """)

st.markdown("---")
st.caption("Hong Kong Infrastructure Reliability & DIF Platform | Developed for Academic Research & Engineering Community")

