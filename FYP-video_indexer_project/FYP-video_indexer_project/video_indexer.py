import requests
import time
import os
from dotenv import load_dotenv

class VideoIndexer:
    def __init__(self):
        load_dotenv()
        
        self.api_key = os.getenv('VIDEO_INDEXER_API_KEY')
        self.account_id = os.getenv('VIDEO_INDEXER_ACCOUNT_ID')
        self.location = os.getenv('VIDEO_INDEXER_LOCATION')
        self.base_url = 'https://api.videoindexer.ai'

    def get_access_token(self):
        """獲取存取令牌"""
        url = f"{self.base_url}/auth/{self.location}/Accounts/{self.account_id}/AccessToken"
        headers = {
            'Ocp-Apim-Subscription-Key': self.api_key
        }
        params = {
            'allowEdit': 'true'
        }
        response = requests.get(url, headers=headers, params=params)
        if response.status_code == 200:
            return response.text.strip('"')  # 移除引號
        else:
            print(f"獲取token失敗: {response.text}")
            return None

    def upload_video(self, video_path, video_name):
        """上傳影片"""
        # 首先獲取存取令牌
        access_token = self.get_access_token()
        if not access_token:
            return None
        
        # 準備上傳
        upload_url = f"{self.base_url}/{self.location}/Accounts/{self.account_id}/Videos"
        headers = {
            'Authorization': f'Bearer {access_token}'
        }
        
        # 準備檔案同參數
        with open(video_path, 'rb') as video_file:
            files = {
                'video': (video_name, video_file, 'video/mp4')
            }
            params = {
                'name': video_name,
                'privacy': 'Private',
                'language': 'zh-HK',
                'accessToken': access_token
            }
            
            # 上傳影片
            response = requests.post(upload_url, headers=headers, files=files, params=params)
            
            if response.status_code == 200:
                return response.json()
            else:
                print(f"上傳失敗: {response.text}")
                return None

    def get_video_info(self, video_id):
        """獲取影片分析結果"""
        access_token = self.get_access_token()
        if not access_token:
            return None
        
        url = f"{self.base_url}/{self.location}/Accounts/{self.account_id}/Videos/{video_id}/Index"
        params = {
            'accessToken': access_token
        }
        
        response = requests.get(url, params=params)
        return response.json()

    def wait_for_processing(self, video_id, timeout=1200):  
        """等待影片處理完成"""
        start_time = time.time()
        while True:
            info = self.get_video_info(video_id)
            if not info:
                return None
                
            state = info.get('state')
            
            if state == 'Processed':
                print("影片處理完成！")
                return info
            elif state == 'Failed':
                print("處理失敗")
                return None
            
            if time.time() - start_time > timeout:
                print("處理超時")
                return None
                
            print(f"處理中... 狀態: {state}")
            time.sleep(10)

def main():
    # 初始化 Video Indexer
    indexer = VideoIndexer()
    
    # 上傳影片
    video_path = "C:/Users/sfa04/OneDrive/桌面/IMG_1716.mp4"
    video_name = "測試影片"
    
    print("開始上傳影片...")
    upload_result = indexer.upload_video(video_path, video_name)
    
    if upload_result:
        video_id = upload_result.get('id')
        print(f"影片上傳成功，ID: {video_id}")
        
        # 等待處理完成同獲取結果
        result = indexer.wait_for_processing(video_id)
        
        if result:
            print("\n分析結果:")
            if 'videos' in result:
                video_info = result['videos'][0]
                print(f"影片長度: {video_info.get('durationInSeconds')}秒")
                
                if 'insights' in video_info:
                    insights = video_info['insights']
                    if 'transcript' in insights:
                        print("\n字幕:")
                        for line in insights['transcript']:
                            print(f"{line['text']} ({line['startTime']} - {line['endTime']})")

if __name__ == "__main__":
    main()