import httpx
from bs4 import BeautifulSoup
from typing import List, Dict

class DCInsideScraper:
    def __init__(self):
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8"
        }

    async def get_recent_posts(self, gallery_id: str, limit: int = 20) -> List[Dict[str, str]]:
        url = f"https://gall.dcinside.com/board/lists/?id={gallery_id}"
        
        async with httpx.AsyncClient(headers=self.headers) as client:
            try:
                response = await client.get(url, timeout=10.0)
                response.raise_for_status()
            except httpx.HTTPError as e:
                # DC인사이드 마이너 갤러리의 경우 url 구조가 다를 수 있으므로 폴백 추가
                url_mgall = f"https://gall.dcinside.com/mgallery/board/lists/?id={gallery_id}"
                try:
                    response = await client.get(url_mgall, timeout=10.0)
                    response.raise_for_status()
                except httpx.HTTPError as e:
                    raise Exception(f"갤러리를 불러오는데 실패했습니다: {gallery_id} (존재하지 않거나 접근 차단됨)")
        
        soup = BeautifulSoup(response.text, "html.parser")
        posts = soup.select("tr.us-post")
        
        result = []
        for post in posts:
            if len(result) >= limit:
                break
                
            post_id_elem = post.select_one("td.gall_num")
            title_elem = post.select_one("td.gall_tit a")
            
            # 공지사항(설자리) 제외
            if post_id_elem and title_elem and post_id_elem.text.strip().isdigit():
                post_id = post_id_elem.text.strip()
                title = title_elem.text.strip()
                # 댓글수 같은 불필요한 텍스트 제거 기능이 필요한 경우 여기서 전처리 가능
                
                result.append({
                    "post_id": f"dc_{gallery_id}_{post_id}",
                    "content": title
                })
                
        return result

scraper_service = DCInsideScraper()
