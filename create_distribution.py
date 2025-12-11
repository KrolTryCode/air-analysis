"""
Создание дистрибутива проекта с QR-кодом
"""
import zipfile
import qrcode
from pathlib import Path
import hashlib
import json
from datetime import datetime


def create_qr_code(url, filename):
    """Создать QR-код для ссылки на дистрибутив"""
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(url)
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="black", back_color="white")
    img.save(filename)
    print(f"✓ QR-код создан: {filename}")


def calculate_checksum(filepath):
    sha256_hash = hashlib.sha256()
    with open(filepath, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()


def create_distribution():
    root = Path(__file__).resolve().parent
    dist_name = "air-quality-analysis-v1.0.0"
    zip_path = root / f"{dist_name}.zip"
    
    # Файлы для включения в дистрибутив
    files_to_include = [
        # Документация
        "requirements.txt",
        "docker-compose.yml",
        "Dockerfile",
        
        # Исходный код
        "air_src/config.py",
        "air_src/db_manager.py",
        "air_src/data_validator.py",
        "air_src/fetch_data.py",
        "air_src/analysis_overview.py",
        "air_src/analysis_city_rankings.py",
        "air_src/analysis_correlations.py",
        "air_src/analysis_seasonality.py",
        "air_src/sarima_forecast.py",
        
        # Тесты
        "tests/__init__.py",
        "tests/test_db_manager.py",
        "tests/test_data_quality.py",
        "tests/test_integration.py"
    ]
    
    print("\nСоздание ZIP-архива...")
    
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for file_path in files_to_include:
            full_path = root / file_path
            if full_path.exists():
                arcname = f"{dist_name}/{file_path}"
                zipf.write(full_path, arcname)
                print(f"  ✓ {file_path}")
            else:
                print(f"  ⚠️  Файл не найден: {file_path}")
        
        # Создать пустую директорию output
        zipf.writestr(f"{dist_name}/output/.gitkeep", "")
    
    # Вычислить контрольную сумму
    checksum = calculate_checksum(zip_path)
    
    # Метаданные дистрибутива
    metadata = {
        "name": "air-quality-analysis",
        "version": "1.0.0",
        "date": datetime.now().isoformat(),
        "size_bytes": zip_path.stat().st_size,
        "size_mb": round(zip_path.stat().st_size / (1024 * 1024), 2),
        "checksum_sha256": checksum,
        "files_count": len(files_to_include),
        "python_version": "3.10+",
        "dependencies": [
            "pandas==2.1.4",
            "numpy==1.26.2",
            "matplotlib==3.8.2",
            "seaborn==0.13.0",
            "pymongo==4.6.1",
            "requests==2.31.0",
            "tqdm==4.66.1",
            "pmdarima==2.0.4",
            "statsmodels==0.14.1"
        ]
    }
    
    # Сохранить метаданные
    metadata_path = root / f"{dist_name}-metadata.json"
    with open(metadata_path, 'w', encoding='utf-8') as f:
        json.dump(metadata, f, indent=2, ensure_ascii=False)
    
    print(f"\n✓ Дистрибутив создан: {zip_path}")
    print(f"✓ Метаданные сохранены: {metadata_path}")
    print(f"✓ Размер: {metadata['size_mb']} MB")
    print(f"✓ SHA256: {checksum[:16]}...")
    
    # Создать QR-код
    # Замените на реальный URL после загрузки на GitHub/GitLab
    github_url = "https://github.com/KrolTryCode/air-analysis/releases"
    qr_path = root / "distribution_qr.png"
    create_qr_code(github_url, qr_path)
    
    # Создать инструкцию по установке
    install_guide = f"""
╔══════════════════════════════════════════════════════════════════╗
║          ИНСТРУКЦИЯ ПО УСТАНОВКЕ ДИСТРИБУТИВА                    ║
╚══════════════════════════════════════════════════════════════════╝

Дистрибутив: {dist_name}.zip
Версия: 1.0.0
Размер: {metadata['size_mb']} MB
SHA256: {checksum}

═══════════════════════════════════════════════════════════════════

📥 СКАЧИВАНИЕ

1. Скачайте дистрибутив одним из способов:
   
   • Прямая ссылка: {github_url}/releases
   • QR-код: См. файл distribution_qr.png
   • Git clone: git clone {github_url}

═══════════════════════════════════════════════════════════════════

📦 УСТАНОВКА

Windows:
--------
1. Распакуйте {dist_name}.zip
2. Откройте командную строку в папке проекта
3. Запустите: setup.bat
4. Следуйте инструкциям на экране

Linux/Mac:
----------
1. Распакуйте {dist_name}.zip
2. Откройте терминал в папке проекта
3. Сделайте скрипт исполняемым: chmod +x setup.sh
4. Запустите: ./setup.sh
5. Следуйте инструкциям на экране

═══════════════════════════════════════════════════════════════════

🚀 БЫСТРЫЙ СТАРТ

После установки:

1. Активируйте виртуальное окружение:
   Windows: venv\\Scripts\\activate
   Linux/Mac: source venv/bin/activate

2. Загрузите данные:
   python src/fetch_data.py

3. Запустите анализ:
   python src/analysis_overview.py
   python src/analysis_rankings.py
   python src/forecast_sarima.py

4. Проверьте качество:
   python run_tests.py
   python quality_report.py

═══════════════════════════════════════════════════════════════════

📚 ДОКУМЕНТАЦИЯ

Полная документация: README.md
Список файлов: MANIFEST.txt
Проблемы: См. раздел "Устранение проблем" в README.md

═══════════════════════════════════════════════════════════════════

✅ ПРОВЕРКА ЦЕЛОСТНОСТИ

Проверьте контрольную сумму после скачивания:

Windows:
certutil -hashfile {dist_name}.zip SHA256

Linux/Mac:
sha256sum {dist_name}.zip

Ожидаемое значение:
{checksum}

═══════════════════════════════════════════════════════════════════
"""
    
    install_guide_path = root / "INSTALL.txt"
    with open(install_guide_path, 'w', encoding='utf-8') as f:
        f.write(install_guide)
    
    print(f"✓ Инструкция по установке: {install_guide_path}")
    
    print("\n" + "=" * 70)
    print("ДИСТРИБУТИВ ГОТОВ К РАСПРОСТРАНЕНИЮ")
    print("=" * 70)
    print(f"\nФайлы для распространения:")
    print(f"  1. {zip_path.name}")
    print(f"  2. {metadata_path.name}")
    print(f"  3. {qr_path.name}")
    print(f"  4. {install_guide_path.name}")
    print(f"\nЗагрузите эти файлы на GitHub/GitLab в раздел Releases")


if __name__ == '__main__':
    create_distribution()