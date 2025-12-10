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
    layout="wide",
    initial_sidebar_state="collapsed"  # スマホでは初期状態で閉じる
)

# カスタムCSS
st.markdown("""
    <style>
    /* メインコンテナのスタイル */
    .main {
        padding-top: 0 !important;
    }
    
    /* 全体的なフォントサイズを小さく */
    .main .block-container {
        padding-top: 0 !important;
        padding-bottom: 1rem;
    }
    
    /* stMainBlockContainerの上余白を削減 */
    .stMainBlockContainer {
        padding-top: 0 !important;
        margin-top: 0 !important;
    }
    
    /* st-emotion-cache-zy6yx3の上余白も削減 */
    .st-emotion-cache-zy6yx3 {
        padding-top: 0 !important;
        margin-top: 0 !important;
    }
    
    /* e4man114クラスの上余白も削減 */
    .e4man114 {
        padding-top: 0 !important;
        margin-top: 0 !important;
    }
    
    /* block-containerクラス全般の上余白を削減 */
    .block-container {
        padding-top: 0 !important;
        margin-top: 0 !important;
    }
    
    /* コンテナの余白を削減 */
    .element-container {
        margin-bottom: 0.2rem;
    }
    
    /* stElementContainerの余白を完全に削除 */
    .stElementContainer {
        margin: 0 !important;
        padding: 0 !important;
        min-height: 0 !important;
        height: auto !important;
        max-height: fit-content !important;
    }
    
    /* st-emotion-cache-18kf3utを中央揃えに */
    .st-emotion-cache-18kf3ut {
        display: flex !important;
        align-items: center !important;
        min-height: 1.8rem !important;
        margin: 0 !important;
        padding: 0 !important;
    }
    
    /* ek2vi384クラスも中央揃えに */
    .ek2vi384 {
        display: flex !important;
        align-items: center !important;
        min-height: 1.8rem !important;
        margin: 0 !important;
        padding: 0 !important;
    }
    
    /* すべてのstから始まる要素コンテナの余白を削減 */
    [class*="stElementContainer"] {
        margin: 0 !important;
        padding: 0 !important;
        min-height: 0 !important;
        max-height: fit-content !important;
    }
    
    /* Streamlitのキャッシュクラスの余白も削除 */
    [class*="st-emotion-cache"] {
        margin-top: 0 !important;
        margin-bottom: 0 !important;
    }
    
    /* st-emotion-cache-pk3c77のmax-widthを制限 */
    .st-emotion-cache-pk3c77 {
        max-width: none !important;
        width: auto !important;
        margin: 0 !important;
        padding: 0 !important;
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
    
    /* 出席ボタンのカスタムスタイル */
    div[data-testid="column"] button[kind="secondary"] {
        width: 100%;
        font-size: 0.85rem;
        padding: 0.3rem 0.5rem;
        border-radius: 8px;
        font-weight: 600;
        transition: all 0.2s ease;
        background-color: #f0f0f0 !important;
        color: #666 !important;
        border: 2px solid #ddd !important;
    }
    
    div[data-testid="column"] button[kind="secondary"]:hover {
        background-color: #e8f5e9 !important;
        border-color: #4caf50 !important;
        color: #2e7d32 !important;
    }
    
    /* 出席済みボタン（Primary）のスタイル - より強力に */
    div[data-testid="column"] button[kind="primary"],
    div[data-testid="column"] button[kind="primary"]:focus,
    div[data-testid="column"] button[kind="primary"]:active {
        width: 100%;
        background: linear-gradient(135deg, #4caf50 0%, #2196f3 100%) !important;
        color: white !important;
        border: none !important;
        font-size: 0.85rem;
        padding: 0.3rem 0.5rem;
        border-radius: 8px;
        font-weight: 600;
        box-shadow: 0 2px 4px rgba(76, 175, 80, 0.3) !important;
        transition: all 0.2s ease;
    }
    
    div[data-testid="column"] button[kind="primary"]:hover {
        transform: translateY(-1px);
        box-shadow: 0 4px 8px rgba(76, 175, 80, 0.4) !important;
        background: linear-gradient(135deg, #66bb6a 0%, #42a5f5 100%) !important;
    }
    
    /* Streamlitのデフォルトprimaryボタンスタイルを上書き */
    button[kind="primary"] {
        background-color: #4caf50 !important;
        background: linear-gradient(135deg, #4caf50 0%, #2196f3 100%) !important;
        border-color: #4caf50 !important;
    }
    
    button[kind="primary"]:hover {
        background-color: #66bb6a !important;
        background: linear-gradient(135deg, #66bb6a 0%, #42a5f5 100%) !important;
        border-color: #66bb6a !important;
    }
    
    button[kind="primary"]:focus,
    button[kind="primary"]:active {
        background-color: #4caf50 !important;
        background: linear-gradient(135deg, #4caf50 0%, #2196f3 100%) !important;
        border-color: #4caf50 !important;
        box-shadow: 0 2px 4px rgba(76, 175, 80, 0.3) !important;
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
        margin-bottom: 0 !important;
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
    
    /* ヘッダー後の要素を上に詰める */
    .header-style + div {
        margin-top: 0 !important;
        padding-top: 0 !important;
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
        border: none;
        border-top: 1px solid #e0e0e0;
        height: 0;
        padding: 0;
    }
    
    /* stMarkdownContainerの高さと余白を削減 */
    .stMarkdownContainer {
        margin: 0 !important;
        padding: 0 !important;
        min-height: 0 !important;
    }
    
    /* カラムの余白を削減 */
    [data-testid="column"] {
        padding-top: 0;
        padding-bottom: 0;
    }
    
    /* スマホ対応 - レスポンシブデザイン */
    @media (max-width: 768px) {
        /* メインコンテナの余白調整 */
        .main .block-container {
            padding-left: 0.3rem;
            padding-right: 0.3rem;
        }
        
        /* ヘッダーのサイズ調整 */
        .header-style {
            padding: 0.5rem;
            margin-bottom: 0.5rem;
        }
        
        .header-style h1 {
            font-size: 1.1rem;
        }
        
        .header-style p {
            font-size: 0.7rem;
        }
        
        /* メトリクスカードを2列に */
        div[data-testid="stHorizontalBlock"] {
            display: grid !important;
            grid-template-columns: 1fr 1fr !important;
            gap: 0.3rem !important;
        }
        
        div[data-testid="metric-container"] {
            width: 100% !important;
            padding: 0.3rem;
        }
        
        div[data-testid="metric-container"] label {
            font-size: 0.7rem;
        }
        
        div[data-testid="metric-container"] [data-testid="stMetricValue"] {
            font-size: 0.95rem;
        }
    }
    
    /* さらに小さい画面（スマホ縦持ち） */
    @media (max-width: 480px) {
        /* ヘッダーをさらに小さく */
        .header-style h1 {
            font-size: 1rem;
        }
        
        .header-style p {
            display: none;
        }
        
        /* メトリクスの値をさらに小さく */
        div[data-testid="metric-container"] label {
            font-size: 0.6rem;
        }
        
        div[data-testid="metric-container"] [data-testid="stMetricValue"] {
            font-size: 0.8rem;
        }
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
    st.markdown('<div class="stats-container">', unsafe_allow_html=True)
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
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown("---")
    
    # テーブル全体を囲む枠
    st.markdown('<div class="table-wrapper">', unsafe_allow_html=True)
    
    # テーブル形式で表示
    st.markdown("""
    <style>
    /* 統計情報を囲む枠 */
    .stats-container {
        background-color: #ffffff;
        border: 2px solid #e0e0e0;
        border-radius: 10px;
        padding: 1rem;
        margin-bottom: 1rem;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    }
    
    /* テーブル全体を囲む枠 */
    .table-wrapper {
        background-color: #ffffff;
        border: 2px solid #1f77b4;
        border-radius: 10px;
        padding: 1rem;
        margin-top: 1rem;
        box-shadow: 0 2px 8px rgba(31, 119, 180, 0.15);
    }
    
    /* ヘッダーを囲む枠 */
    .header-wrapper {
        background-color: #f8f9fa;
        border: 1px solid #dee2e6;
        border-radius: 8px;
        padding: 0.5rem;
        margin-bottom: 1rem;
    }
    
    /* レコードをまとめる枠 */
    .records-wrapper {
        background-color: #ffffff;
        border: 1px solid #e0e0e0;
        border-radius: 8px;
        padding: 0.5rem;
        max-height: 600px;
        overflow-y: auto;
    }
    
    .attendance-table-container {
        width: 100%;
        display: flex;
        flex-direction: column;
        align-items: center;
    }
    
    .attendance-row {
        display: flex !important;
        flex-direction: row !important;
        flex-wrap: nowrap !important;
        align-items: center !important;
        width: 100% !important;
        border-bottom: 1px solid #eee;
        padding: 0.2rem 0;
        min-height: 2.5rem;
        gap: 0;
    }
    
    /* attendance-row内の全ての子要素をflexアイテムに */
    .attendance-row > * {
        flex-shrink: 0 !important;
    }
    
    .attendance-header {
        display: flex;
        align-items: center;
        justify-content: center;
        width: 100%;
        margin-left: auto;
        margin-right: auto;
        font-weight: bold;
        background-color: #1f77b4;
        color: white;
        padding: 0.5rem 0;
        border-radius: 5px;
        margin-bottom: 0.5rem;
    }

    .stElementContainer {
        margin: 0 !important;
        padding: 0 !important;
        padding-right: 0 !important;
        margin-right: 0 !important;
        min-height: 0 !important;
        height: auto !important;
        max-height: fit-content !important;
    }

    /* セル内のstElementContainerの右余白も削除 */
    .att-cell-first .stElementContainer,
    .att-cell-second .stElementContainer,
    .att-cell-delete .stElementContainer {
        margin: 0 !important;
        padding: 0 !important;
        min-height: 0 !important;
        height: auto !important;
        max-height: fit-content !important;
    }
    
    .att-cell-no {
        flex: 0 0 8% !important;
        max-width: 8% !important;
        text-align: center;
        font-size: 1rem;
        padding: 0 0.2rem;
    }
    
    .att-cell-name {
        flex: 0 0 25% !important;
        max-width: 25% !important;
        text-align: center;
        font-weight: bold;
        font-size: 1rem;
        padding: 0 0.5rem;
    }
    
    .att-cell-first {
        flex: 0 0 25% !important;
        max-width: 25% !important;
        text-align: center;
        font-size: 1rem;
        padding: 0 0.2rem;
    }
    
    .att-cell-second {
        flex: 0 0 25% !important;
        max-width: 25% !important;
        text-align: center;
        font-size: 1rem;
        padding: 0 0.2rem;
    }
    
    .att-cell-delete {
        flex: 0 0 10% !important;
        max-width: 10% !important;
        text-align: center;
        font-size: 1rem;
        padding: 0 0.2rem;
    }
    
    /* ヘッダーの各セルの文字サイズを統一 */
    .attendance-header .att-cell-no,
    .attendance-header .att-cell-name,
    .attendance-header .att-cell-first,
    .attendance-header .att-cell-second,
    .attendance-header .att-cell-delete {
        font-size: 1rem;
    }
    
    /* Noと名前のstMarkdownブロックをインライン化 */
    .attendance-row > .stMarkdown,
    .attendance-row > div[data-testid="stMarkdown"],
    .attendance-row > div[data-testid="stMarkdownContainer"] {
        display: inline-block !important;
        width: auto !important;
        margin: 0 !important;
        padding: 0 !important;
    }
    
    /* attendance-row直下の全てのdivをインライン化 */
    .attendance-row > div {
        display: inline-block !important;
        margin: 0 !important;
        padding: 0 !important;
    }
    
    /* att-cell-*が含まれるdivはインライン */
    div[class*="att-cell-"] {
        display: inline-block !important;
        vertical-align: middle !important;
    }
    
    /* attendance-row内のst-emotion-cache-pk3c77を制限 */
    .attendance-row .st-emotion-cache-pk3c77 {
        max-width: none !important;
        width: auto !important;
        display: inline-block !important;
        margin: 0 !important;
        padding: 0 !important;
    }
    
    /* attendance-row内のすべてのst-emotion-cacheクラスを制限 */
    .attendance-row [class*="st-emotion-cache"] {
        max-width: none !important;
        width: auto !important;
        margin: 0 !important;
        padding: 0 !important;
    }
    
    /* ボタンコンテナもFlexboxに */
    .att-btn-container {
        display: flex !important;
        align-items: center !important;
        width: 100% !important;
    }
    
    /* 出席ボタン専用のスタイル */
    .att-cell-first button,
    .att-cell-second button {
        font-size: 0.7rem !important;
        padding: 0.2rem 0.3rem !important;
        height: 1.8rem !important;
        min-height: 1.8rem !important;
        line-height: 1.2 !important;
        white-space: nowrap !important;
        width: 100% !important;
    }
    
    /* 削除ボタン専用のスタイル */
    .att-cell-delete button {
        font-size: 1rem !important;
        padding: 0.1rem 0.3rem !important;
        height: 1.8rem !important;
        min-height: 1.8rem !important;
        width: 100% !important;
    }
    
    /* 出席ボタンのPrimary/Secondaryスタイル */
    .att-cell-first button[kind="primary"],
    .att-cell-second button[kind="primary"] {
        background: linear-gradient(135deg, #4caf50 0%, #2196f3 100%) !important;
        color: white !important;
        border: none !important;
        box-shadow: 0 1px 2px rgba(76, 175, 80, 0.3) !important;
    }
    
    .att-cell-first button[kind="secondary"],
    .att-cell-second button[kind="secondary"] {
        background-color: #f0f0f0 !important;
        color: #666 !important;
        border: 1px solid #ddd !important;
    }
    
    /* Streamlitのデフォルトコンテナを無効化 */
    .att-cell-first > div,
    .att-cell-second > div,
    .att-cell-delete > div {
        width: 100% !important;
        margin: 0 !important;
        padding: 0 !important;
    }
    
    @media (max-width: 768px) {
        .stats-container {
            padding: 0.5rem;
            margin-bottom: 0.5rem;
        }
        
        .table-wrapper {
            padding: 0.5rem;
            margin-top: 0.5rem;
        }
        
        .header-wrapper {
            padding: 0.3rem;
            margin-bottom: 0.5rem;
        }
        
        .records-wrapper {
            padding: 0.3rem;
            max-height: 400px;
        }
        
        .att-cell-no { flex: 0 0 8% !important; max-width: 8% !important; font-size: 0.75rem; }
        .att-cell-name { flex: 0 0 25% !important; max-width: 25% !important; font-size: 0.75rem; }
        .att-cell-first { flex: 0 0 25% !important; max-width: 25% !important; }
        .att-cell-second { flex: 0 0 25% !important; max-width: 25% !important; }
        .att-cell-delete { flex: 0 0 10% !important; max-width: 10% !important; }
        
        /* ヘッダーの文字サイズも統一 */
        .attendance-header .att-cell-no,
        .attendance-header .att-cell-name,
        .attendance-header .att-cell-first,
        .attendance-header .att-cell-second,
        .attendance-header .att-cell-delete {
            font-size: 0.75rem;
        }
        
        .att-cell-first button,
        .att-cell-second button {
            font-size: 0.65rem !important;
            padding: 0.15rem 0.2rem !important;
            height: 1.6rem !important;
            min-height: 1.6rem !important;
        }
    }
    
    @media (max-width: 480px) {
        .stats-container {
            padding: 0.3rem;
        }
        
        .table-wrapper {
            padding: 0.3rem;
            margin-top: 0.3rem;
        }
        
        .header-wrapper {
            padding: 0.2rem;
            margin-bottom: 0.3rem;
        }
        
        .records-wrapper {
            padding: 0.2rem;
            max-height: 300px;
        }
        
        .attendance-row { padding: 0.15rem 0; min-height: 2.2rem; }
        .att-cell-no { flex: 0 0 8% !important; max-width: 8% !important; font-size: 0.7rem; padding: 0 0.1rem; }
        .att-cell-name { flex: 0 0 25% !important; max-width: 25% !important; font-size: 0.7rem; padding: 0 0.2rem; }
        .att-cell-first { flex: 0 0 25% !important; max-width: 25% !important; }
        .att-cell-second { flex: 0 0 25% !important; max-width: 25% !important; }
        .att-cell-delete { flex: 0 0 10% !important; max-width: 10% !important; }
        
        /* ヘッダーの文字サイズも統一 */
        .attendance-header .att-cell-no,
        .attendance-header .att-cell-name,
        .attendance-header .att-cell-first,
        .attendance-header .att-cell-second,
        .attendance-header .att-cell-delete {
            font-size: 0.7rem;
        }
        
        .att-cell-first button,
        .att-cell-second button {
            font-size: 0.6rem !important;
            padding: 0.1rem 0.15rem !important;
            height: 1.5rem !important;
            min-height: 1.5rem !important;
        }
        
        .att-cell-delete button {
            font-size: 0.9rem !important;
            height: 1.5rem !important;
            min-height: 1.5rem !important;
        }
    }
    </style>
    """, unsafe_allow_html=True)
    
    # ヘッダー行
    st.markdown("""
    <div class="header-wrapper">
    <div class="attendance-header">
        <div class="att-cell-no">No</div>
        <div class="att-cell-name">名前</div>
        <div class="att-cell-first">1次会</div>
        <div class="att-cell-second">2次会</div>
        <div class="att-cell-delete">削除</div>
    </div>
    </div>
    """, unsafe_allow_html=True)
    
    # レコードをまとめる枠の開始
    st.markdown('<div class="records-wrapper">', unsafe_allow_html=True)
    
    # 出席簿フォーム
    changes_made = False
    
    for idx, row in df.iterrows():
        # 1行全体をHTMLで作成
        st.markdown(f'<div class="attendance-row">', unsafe_allow_html=True)
        st.markdown(f'<div class="att-cell-no">{row["No"]}</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="att-cell-name">{row["名前"]}</div>', unsafe_allow_html=True)
        
        # 1次会ボタンのセル
        st.markdown('<div class="att-cell-first">', unsafe_allow_html=True)
        if row["1次会"]:
            button_label = "✓ 出席"
            button_type = "primary"
        else:
            button_label = "出席"
            button_type = "secondary"
        
        if st.button(button_label, key=f"first_{row['No']}", type=button_type):
            df.at[idx, "1次会"] = not row["1次会"]
            df.at[idx, "更新日時"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            changes_made = True
        st.markdown('</div>', unsafe_allow_html=True)
        
        # 2次会ボタンのセル
        st.markdown('<div class="att-cell-second">', unsafe_allow_html=True)
        if row["2次会"]:
            button_label = "✓ 出席"
            button_type = "primary"
        else:
            button_label = "出席"
            button_type = "secondary"
        
        if st.button(button_label, key=f"second_{row['No']}", type=button_type):
            df.at[idx, "2次会"] = not row["2次会"]
            df.at[idx, "更新日時"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            changes_made = True
        st.markdown('</div>', unsafe_allow_html=True)
        
        # 削除ボタンのセル
        st.markdown('<div class="att-cell-delete">', unsafe_allow_html=True)
        confirm_key = f"confirm_delete_{row['No']}"
        if confirm_key not in st.session_state:
            st.session_state[confirm_key] = False
        
        if st.button("🗑️", key=f"delete_{row['No']}", help="削除"):
            st.session_state[confirm_key] = True
        st.markdown('</div>', unsafe_allow_html=True)
        
        # 行を閉じる
        st.markdown('</div>', unsafe_allow_html=True)
        
        # 削除確認ダイアログ
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
    
    # 変更を保存
    if changes_made:
        if save_data(sheet, df):
            st.success("✅ 変更を保存しました")
            time.sleep(0.5)
            st.rerun()
    
    # レコード枠とテーブル全体の枠を閉じる
    st.markdown('</div>', unsafe_allow_html=True)  # records-wrapper
    st.markdown('</div>', unsafe_allow_html=True)  # table-wrapper

if __name__ == "__main__":
    main()
