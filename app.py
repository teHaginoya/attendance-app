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

# カスタムCSS
st.markdown("""
    <style>
    /* メインコンテナのスタイル */
    .main {
        padding-top: 1rem;
    }
    
    /* 全体的なフォントサイズを小さく */
    .main .block-container {
        padding-top: 1rem;
        padding-bottom: 1rem;
    }
    
    /* コンテナの余白を削減 */
    .element-container {
        margin-bottom: 0.2rem;
    }
    
    /* stElementContainerの余白を完全に削除 */
    .stElementContainer {
        margin: 0 !important;
        padding: 0 !important;
    }
    
    div.st-emotion-cache-3pwa5w {
        margin: 0 !important;
        padding: 0 !important;
    }
    
    /* ek2vi381クラスの余白も削除 */
    .ek2vi381 {
        margin: 0 !important;
        padding: 0 !important;
    }
    
    /* すべてのstから始まる要素コンテナの余白を削減 */
    [class*="stElementContainer"] {
        margin: 0 !important;
        padding: 0 !important;
    }
    
    /* Streamlitのキャッシュクラスの余白も削除 */
    [class*="st-emotion-cache"] {
        margin-top: 0 !important;
        margin-bottom: 0 !important;
    }
    
    /* 行間の余白を削減 */
    .row-widget {
        margin-bottom: 0.3rem;
    }
    
    /* 入力フィールドのサイズを小さく */
    .stTextInput input {
        font-size: 0.9rem;
        padding: 0.2rem 0.4rem;
        height: 1.8rem;
        margin-bottom: 0;
    }
    
    .stTextInput > div {
        margin-bottom: 0;
    }
    
    /* チェックボックスのサイズと余白を小さく */
    .stCheckbox {
        font-size: 0.85rem;
        margin-bottom: 0;
        padding: 0;
    }
    
    .stCheckbox > label {
        margin-bottom: 0;
        padding: 0.2rem 0;
    }
    
    /* ボタンのサイズを小さく */
    .stButton button {
        font-size: 0.85rem;
        padding: 0.2rem 0.6rem;
        border-radius: 5px;
        transition: all 0.3s ease;
        margin-bottom: 0;
    }
    
    .stButton {
        margin-bottom: 0;
    }
    
    /* メトリクスカードのスタイル */
    div[data-testid="metric-container"] {
        background-color: #f0f8ff;
        border-radius: 8px;
        padding: 0.4rem;
        border: 2px solid #1f77b4;
    }
    
    div[data-testid="metric-container"] label {
        font-size: 0.85rem;
    }
    
    div[data-testid="metric-container"] [data-testid="stMetricValue"] {
        font-size: 1.2rem;
    }
    
    /* ヘッダーのスタイル */
    .header-style {
        background: linear-gradient(90deg, #1f77b4 0%, #3498db 100%);
        padding: 0.8rem;
        border-radius: 10px;
        color: white;
        margin-bottom: 0.8rem;
    }
    
    .header-style h1 {
        font-size: 1.5rem;
        margin: 0;
    }
    
    .header-style p {
        font-size: 0.9rem;
        margin: 0;
        opacity: 0.9;
    }
    
    /* テキストのサイズを小さく */
    .stMarkdown {
        font-size: 0.9rem;
        margin-bottom: 0.3rem;
    }
    
    /* セレクトボックスのサイズを小さく */
    .stSelectbox select {
        font-size: 0.9rem;
        padding: 0.3rem 0.5rem;
    }
    
    /* dividerの余白を大幅に減らす */
    hr {
        margin-top: 0.1rem;
        margin-bottom: 0.1rem;
    }
    
    /* カラムの余白を削減 */
    [data-testid="column"] {
        padding-top: 0;
        padding-bottom: 0;
    }
    
    /* コンテナの余白を削減 */
    [data-testid="stVerticalBlock"] > [style*="flex-direction: column;"] > [data-testid="stVerticalBlock"] {
        gap: 0.1rem;
    }
    
    /* stContainerの余白を削除 */
    [data-testid="stVerticalBlock"] > div {
        gap: 0.1rem;
    }
    </style>
""", unsafe_allow_html=True)

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
            return pd.DataFrame(columns=["No", "名前", "1次会", "2次会", "コメント", "更新日時"])
        
        df = pd.DataFrame(data)
        
        # 古い形式から新しい形式への変換
        if "ID" in df.columns and "No" not in df.columns:
            df = df.rename(columns={"ID": "No"})
        
        if "出席" in df.columns and "1次会" not in df.columns:
            # 出席列を1次会に変換、2次会は新規作成
            df = df.rename(columns={"出席": "1次会"})
            df["2次会"] = False
        
        # 必須カラムの確認と追加
        required_columns = ["No", "名前", "1次会", "2次会", "コメント", "更新日時"]
        for col in required_columns:
            if col not in df.columns:
                if col in ["1次会", "2次会"]:
                    df[col] = False
                else:
                    df[col] = ""
        
        # 出席列をブール型に変換
        if "1次会" in df.columns:
            df["1次会"] = df["1次会"].astype(str).str.upper() == "TRUE"
        if "2次会" in df.columns:
            df["2次会"] = df["2次会"].astype(str).str.upper() == "TRUE"
        
        # カラムの順序を統一
        df = df[required_columns]
        
        return df
    except Exception as e:
        st.error(f"データ読み込みエラー: {e}")
        return pd.DataFrame(columns=["No", "名前", "1次会", "2次会", "コメント", "更新日時"])

def save_data(sheet, df):
    """DataFrameをスプレッドシートに保存"""
    try:
        # 出席列をTRUE/FALSEの文字列に変換
        df_copy = df.copy()
        df_copy["1次会"] = df_copy["1次会"].apply(lambda x: "TRUE" if x else "FALSE")
        df_copy["2次会"] = df_copy["2次会"].apply(lambda x: "TRUE" if x else "FALSE")
        
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
    # タイトル
    st.markdown('<div class="header-style"><h1>📝 出席簿アプリ</h1><p>参加者の出席状況を管理</p></div>', unsafe_allow_html=True)
    
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
    
    # サイドバー
    with st.sidebar:
        st.header("➕ 新規参加者追加")
        new_name = st.text_input("名前", key="new_name_input")
        if st.button("追加", type="primary", use_container_width=True):
            if new_name:
                df = load_data(sheet)
                new_no = df["No"].max() + 1 if len(df) > 0 else 1
                new_row = pd.DataFrame([{
                    "No": new_no,
                    "名前": new_name,
                    "1次会": False,
                    "2次会": False,
                    "コメント": "",
                    "更新日時": ""
                }])
                df = pd.concat([df, new_row], ignore_index=True)
                if save_data(sheet, df):
                    st.success(f"✅ {new_name}さんを追加しました！")
                    time.sleep(1)
                    st.rerun()
            else:
                st.warning("⚠️ 名前を入力してください")
        
        st.markdown("---")
        
        # ソート機能
        st.header("🔄 表示順序")
        sort_option = st.selectbox(
            "並び替え",
            ["No順", "名前順（あいうえお）", "1次会出席者優先", "2次会出席者優先"],
            key="sort_option"
        )
        
        st.markdown("---")
        
        st.header("🔄 データ更新")
        if st.button("最新データを取得", use_container_width=True):
            st.rerun()
        
        st.markdown("---")
        st.info("💡 ヒント: 複数人で同時に使用する場合は、定期的に「最新データを取得」ボタンを押してください。")
    
    # データ読み込み
    df = load_data(sheet)
    
    if len(df) == 0:
        st.info("👥 参加者がいません。サイドバーから追加してください。")
        return
    
    # ソート処理
    try:
        if sort_option == "No順":
            df = df.sort_values("No")
        elif sort_option == "名前順（あいうえお）":
            df = df.sort_values("名前")
        elif sort_option == "1次会出席者優先":
            df = df.sort_values(["1次会", "No"], ascending=[False, True])
        elif sort_option == "2次会出席者優先":
            df = df.sort_values(["2次会", "No"], ascending=[False, True])
        
        df = df.reset_index(drop=True)
    except Exception as e:
        st.warning(f"ソートエラー: {e}")
        # ソートに失敗してもそのまま表示を続ける
    
    # 統計情報
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("👥 総参加者数", len(df))
    with col2:
        first_attended = df["1次会"].sum()
        st.metric("🍻 1次会出席", f"{first_attended}名")
    with col3:
        second_attended = df["2次会"].sum()
        st.metric("🎉 2次会出席", f"{second_attended}名")
    with col4:
        both_attended = ((df["1次会"]) & (df["2次会"])).sum()
        st.metric("⭐ 両方出席", f"{both_attended}名")
    
    st.markdown("---")
    
    # テーブルヘッダー
    header_cols = st.columns([0.8, 2.5, 1.2, 1.2, 3, 0.8])
    headers = ["No", "名前", "1次会", "2次会", "コメント", "削除"]
    for col, header in zip(header_cols, headers):
        with col:
            st.markdown(f"<div style='font-size:0.9rem;'><strong>{header}</strong></div>", unsafe_allow_html=True)
    
    # 出席簿フォーム
    changes_made = False
    
    for idx, row in df.iterrows():
        # レコード全体の余白を最小化
        col1, col2, col3, col4, col5, col6 = st.columns([0.8, 2.5, 1.2, 1.2, 3, 0.8])
        
        with col1:
            st.markdown(f"<div style='padding:0; margin:0; line-height:1.8rem; font-size:0.9rem;'><strong>{row['No']}</strong></div>", unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"<div style='padding:0; margin:0; line-height:1.8rem; font-size:0.9rem;'><strong>{row['名前']}</strong></div>", unsafe_allow_html=True)
        
        with col3:
            first_party = st.checkbox(
                "1次会",
                value=row["1次会"],
                key=f"first_{row['No']}",
                label_visibility="collapsed"
            )
        
        with col4:
            second_party = st.checkbox(
                "2次会",
                value=row["2次会"],
                key=f"second_{row['No']}",
                label_visibility="collapsed"
            )
        
        with col5:
            comment = st.text_input(
                "コメント",
                value=row["コメント"],
                key=f"comment_{row['No']}",
                label_visibility="collapsed",
                placeholder="コメントを入力..."
            )
        
        with col6:
            # 削除確認用のセッションステート
            confirm_key = f"confirm_delete_{row['No']}"
            if confirm_key not in st.session_state:
                st.session_state[confirm_key] = False
            
            # 削除ボタン
            if st.button("🗑️", key=f"delete_{row['No']}", help="削除"):
                st.session_state[confirm_key] = True
            
            # 確認ダイアログ
            if st.session_state[confirm_key]:
                st.warning(f"⚠️ {row['名前']}さんを削除しますか？")
                col_yes, col_no = st.columns(2)
                with col_yes:
                    if st.button("はい", key=f"yes_{row['No']}", type="primary"):
                        df = df[df["No"] != row["No"]]
                        if save_data(sheet, df):
                            st.session_state[confirm_key] = False
                            st.success("✅ 削除しました")
                            time.sleep(1)
                            st.rerun()
                with col_no:
                    if st.button("いいえ", key=f"no_{row['No']}"):
                        st.session_state[confirm_key] = False
                        st.rerun()
        
        # 変更があったか確認
        if (first_party != row["1次会"] or 
            second_party != row["2次会"] or 
            comment != row["コメント"]):
            df.at[idx, "1次会"] = first_party
            df.at[idx, "2次会"] = second_party
            df.at[idx, "コメント"] = comment
            df.at[idx, "更新日時"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            changes_made = True
        
        st.divider()
    
    # 変更を保存
    if changes_made:
        if save_data(sheet, df):
            st.success("✅ 変更を保存しました")
            time.sleep(0.5)
            st.rerun()

if __name__ == "__main__":
    main()
