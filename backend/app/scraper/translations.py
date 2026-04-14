TRANSMISSION: dict[str, str] = {
    "AT": "Автомат",
    "MT": "Механика",
    "CVT": "Вариатор",
    "AT(セレクトレバー)": "Автомат",
    "セミAT": "Робот",
    "インパネCVT": "Вариатор",
    "フロアCVT": "Вариатор",
    "フロアAT": "Автомат",
    "フロアMT": "Механика",
    "インパネAT": "Автомат",
    "2ペダルMT": "Робот",
    "シーケンシャルAT": "Автомат",
    "デュアルクラッチAT": "Робот",
}

BODY_TYPE: dict[str, str] = {
    "セダン": "Sedan",
    "SUV": "SUV",
    "ミニバン": "Minivan",
    "ハッチバック": "Hatchback",
    "クーペ": "Coupe",
    "ステーションワゴン": "Wagon",
    "軽自動車": "Kei Car",
    "トラック": "Truck",
    "バン": "Van",
    "オープン": "Convertible",
    "クロスカントリー": "SUV",
    "コンパクトカー": "Hatchback",
    "デリバリーバン": "Van",
}

FUEL_TYPE: dict[str, str] = {
    "ガソリン": "Бензин",
    "ディーゼル": "Дизель",
    "ハイブリッド": "Гибрид",
    "電気": "Электро",
    "プラグインハイブリッド": "Plug-in Hybrid",
    "マイルドハイブリッド": "Mild Hybrid",
    "LPG": "LPG",
    "CNG": "CNG",
}

DRIVE_TYPE: dict[str, str] = {
    "FF": "Передний",
    "FR": "Задний",
    "4WD": "Полный",
    "AWD": "Полный",
    "2WD": "Задний",
    "MR": "Среднемоторный",
    "RR": "Заднемоторный",
    "前輪駆動(FF)": "Передний",
    "後輪駆動(FR)": "Задний",
    "4輪駆動(4WD)": "Полный",
}

ACCIDENT_HISTORY: dict[str, bool | None] = {
    "なし": False,
    "あり": True,
    "－": None,
    "不明": None,
}

# Коды марок в URL сайта
BRAND_CODES: dict[str, str] = {
    "bTO": "Toyota",
    "bNI": "Nissan",
    "bHO": "Honda",
    "bMI": "Mitsubishi",
    "bVW": "Volkswagen",
    "bSU": "Subaru",
    "bMA": "Mazda",
    "bDA": "Daihatsu",
    "bSZ": "Suzuki",
    "bLE": "Lexus",
}

# Японские ключи таблицы характеристик → поля модели
FIELD_MAP: dict[str, str] = {
    "年式": "year",
    "年式(初度登録年)": "year",
    "走行距離": "mileage",
    "ボディタイプ": "body_type",
    "色": "color",
    "排気量": "engine_volume",
    "エンジン種別": "fuel_type",
    "ミッション": "transmission",
    "修復歴": "has_accidents",
    "支払総額（税込）": "price",
    "※内：車両本体価格": "base_price",  # не сохраняем
    "駆動方式": "drive_type",
    "ドア数": "doors",               # не сохраняем
    "乗車定員": "seats",             # не сохраняем
}
