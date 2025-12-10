import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
import pandas as pd
from datetime import datetime
import time

# ページ設定
st.set_page_config(
    page_title="出席簿アプリ",
    page_icon="📝",
    layout="wide"
)

# Google Sheets接続設定
@st.cache_resource
def get_google_sheets_client():
    """Google Sheetsクライアントを取得（キャッシュ）"""
    try:
        # Streamlit Cloudの場合はsecretsから取得
        credentials_dict = st.secrets["gcp_service_account"]
        
        scopes = [
            "https://www.googleapis.com/auth/spreadsheets",
            "https://www.googleapis.com/auth/drive"
        ]
        
        credentials = Credentials.from_service_account_info(
            credentials_dict,
            scopes=scopes
        )
        
        return gspread.authorize(credentials)
    except Exception as e:
        st.error(f"Google Sheets接続エラー: {e}")
        return None

def load_data(sheet):
    """スプレッドシートからデータを読み込む"""
    try:
        data = sheet.get_all_records()
        if not data:
            # データが空の場合は空のDataFrameを返す
            return pd.DataFrame(columns=["ID", "名前", "出席", "コメント", "更新日時"])
        
        df = pd.DataFrame(data)
        # 出席列をブール型に変換
        if "出席" in df.columns:
            df["出席"] = df["出席"].astype(str).str.upper() == "TRUE"
        return df
    except Exception as e:
        st.error(f"データ読み込みエラー: {e}")
        return pd.DataFrame(columns=["ID", "名前", "出席", "コメント", "更新日時"])

def save_data(sheet, df):
    """DataFrameをスプレッドシートに保存"""
    try:
        # 出席列をTRUE/FALSEの文字列に変換
        df_copy = df.copy()
        df_copy["出席"] = df_copy["出席"].apply(lambda x: "TRUE" if x else "FALSE")
        
        # ヘッダーとデータを結合
        data_to_save = [df_copy.columns.tolist()] + df_copy.values.tolist()
        
        # スプレッドシート全体を更新
        sheet.clear()
        sheet.update(data_to_save, value_input_option='RAW')
        return True
    except Exception as e:
        st.error(f"データ保存エラー: {e}")
        return False

def main():
    st.title("📝 出席簿アプリ")
    st.markdown("---")
    
    # Google Sheetsクライアント取得
    client = get_google_sheets_client()
    if not client:
        st.error("Google Sheetsに接続できません。設定を確認してください。")
        return
    
    # スプレッドシートID（secretsから取得）
    try:
        spreadsheet_id = st.secrets["spreadsheet_id"]
    except:
        st.error("スプレッドシートIDが設定されていません。")
        return
    
    # スプレッドシートを開く
    try:
        spreadsheet = client.open_by_key(spreadsheet_id)
        sheet = spreadsheet.sheet1  # 最初のシートを使用
    except Exception as e:
        st.error(f"スプレッドシートを開けません: {e}")
        return
    
    # サイドバー：新規参加者追加
    with st.sidebar:
        st.header("➕ 新規参加者追加")
        new_name = st.text_input("名前")
        if st.button("追加", type="primary"):
            if new_name:
                df = load_data(sheet)
                new_id = df["ID"].max() + 1 if len(df) > 0 else 1
                new_row = pd.DataFrame([{
                    "ID": new_id,
                    "名前": new_name,
                    "出席": False,
                    "コメント": "",
                    "更新日時": ""
                }])
                df = pd.concat([df, new_row], ignore_index=True)
                if save_data(sheet, df):
                    st.success(f"{new_name}さんを追加しました！")
                    time.sleep(1)
                    st.rerun()
            else:
                st.warning("名前を入力してください")
        
        st.markdown("---")
        st.header("🔄 更新")
        if st.button("最新データを取得", use_container_width=True):
            st.rerun()
        
        st.markdown("---")
        st.info("💡 ヒント: 複数人で同時に使用する場合は、定期的に「最新データを取得」ボタンを押してください。")
    
    # メインエリア：出席簿表示
    st.header("📋 出席状況")
    
    # データ読み込み
    df = load_data(sheet)
    
    if len(df) == 0:
        st.info("参加者がいません。サイドバーから追加してください。")
        return
    
    # 出席状況の統計表示
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("総参加者数", len(df))
    with col2:
        attended = df["出席"].sum()
        st.metric("出席者数", attended)
    with col3:
        attendance_rate = (attended / len(df) * 100) if len(df) > 0 else 0
        st.metric("出席率", f"{attendance_rate:.1f}%")
    
    st.markdown("---")
    
    # 出席簿フォーム
    changes_made = False
    
    for idx, row in df.iterrows():
        with st.container():
            col1, col2, col3, col4 = st.columns([1, 3, 4, 1])
            
            with col1:
                st.write(f"**ID: {row['ID']}**")
            
            with col2:
                st.write(f"### {row['名前']}")
            
            with col3:
                # チェックボックス
                attended = st.checkbox(
                    "出席",
                    value=row["出席"],
                    key=f"attend_{row['ID']}"
                )
                
                # コメント入力
                comment = st.text_input(
                    "コメント",
                    value=row["コメント"],
                    key=f"comment_{row['ID']}",
                    label_visibility="collapsed",
                    placeholder="コメントを入力..."
                )
                
                # 変更があったか確認
                if attended != row["出席"] or comment != row["コメント"]:
                    df.at[idx, "出席"] = attended
                    df.at[idx, "コメント"] = comment
                    df.at[idx, "更新日時"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    changes_made = True
            
            with col4:
                # 削除ボタン
                if st.button("🗑️", key=f"delete_{row['ID']}", help="削除"):
                    df = df[df["ID"] != row["ID"]]
                    if save_data(sheet, df):
                        st.success("削除しました")
                        time.sleep(1)
                        st.rerun()
            
            st.markdown("---")
    
    # 変更を保存
    if changes_made:
        if save_data(sheet, df):
            st.success("✅ 変更を保存しました")
            time.sleep(0.5)
            st.rerun()

if __name__ == "__main__":
    main()
