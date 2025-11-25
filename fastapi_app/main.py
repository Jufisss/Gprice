from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import requests
from bs4 import BeautifulSoup
import re

app = FastAPI(title="Steam Wishlist API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class SteamParser:
    @staticmethod
    def search_games(query):
        """Поиск игр в Steam Store"""
        try:
            url = f"https://store.steampowered.com/search/?term={query}"
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            games = []
            
            search_results = soup.find_all('a', class_='search_result_row')[:10]
            
            for result in search_results:
                try:
                    # Извлекаем app_id из ссылки
                    href = result.get('href', '')
                    app_id_match = re.search(r'app/(\d+)', href)
                    if not app_id_match:
                        continue
                    
                    app_id = app_id_match.group(1)
                    
                    # Название игры
                    title_elem = result.find('span', class_='title')
                    title = title_elem.text.strip() if title_elem else "Unknown"
                    
                    # Цена
                    price = 0.0
                    original_price = 0.0
                    discount_percent = 0
                    
                    # Проверяем есть ли скидка
                    discount_element = result.find('div', class_='discount_pct')
                    if discount_element:
                        discount_text = discount_element.text.strip().replace('%', '').replace('-', '')
                        try:
                            discount_percent = int(discount_text) if discount_text else 0
                        except ValueError:
                            discount_percent = 0
                    
                    # Финальная цена (со скидкой)
                    final_price_element = result.find('div', class_='discount_final_price')
                    if final_price_element and final_price_element.text.strip():
                        price_text = final_price_element.text.strip()
                        price = SteamParser._parse_price(price_text)
                    
                    # Оригинальная цена
                    original_price_element = result.find('div', class_='discount_original_price')
                    if original_price_element and original_price_element.text.strip():
                        original_price_text = original_price_element.text.strip()
                        original_price = SteamParser._parse_price(original_price_text)
                    else:
                        original_price = price
                    
                    # Изображение
                    img_elem = result.find('img')
                    image_url = img_elem.get('src') if img_elem else ''
                    
                    games.append({
                        'steam_app_id': int(app_id),
                        'name': title,
                        'current_price': price,
                        'original_price': original_price,
                        'discount_percent': discount_percent,
                        'image_url': image_url,
                        'store_url': href
                    })
                    
                except Exception as e:
                    continue
                    
            return games
            
        except Exception as e:
            print(f"Ошибка при поиске игр: {e}")
            return []
    
    @staticmethod
    def _parse_price(price_text):
        """Парсит цену из строки"""
        try:
            cleaned = re.sub(r'[^\d.,]', '', price_text)
            cleaned = cleaned.replace(',', '.')
            return float(cleaned) if cleaned else 0.0
        except (ValueError, TypeError):
            return 0.0

@app.get("/")
async def root():
    return {"message": "Steam Wishlist FastAPI Service"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "fastapi"}

@app.get("/search/steam")
async def search_steam_games(q: str, limit: int = 10):
    """Поиск игр в Steam через FastAPI"""
    if len(q) < 2:
        return {"error": "Слишком короткий запрос. Минимум 2 символа."}
    
    try:
        steam_games = SteamParser.search_games(q)[:limit]
        return steam_games
    except Exception as e:
        return {"error": f"Ошибка при поиске: {str(e)}"}