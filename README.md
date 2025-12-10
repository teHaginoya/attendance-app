# 出席簿アプリ

Google SheetsとStreamlitを使った出席管理アプリです。

## 機能

- ✅ チェックボックスで出席管理
- 💬 各参加者へのコメント機能
- ➕ 新規参加者の追加
- 🗑️ 参加者の削除
- 📊 出席率の表示
- 🔄 複数人でのデータ共有（Google Sheets経由）

## セットアップ手順

### 1. Google Cloud Platformの設定

1. [Google Cloud Console](https://console.cloud.google.com/)にアクセス
2. 新しいプロジェクトを作成
3. Google Sheets API と Google Drive API を有効化
4. サービスアカウントを作成
5. JSONキーをダウンロード

### 2. Google Sheetsの準備

1. 新しいスプレッドシートを作成
2. 以下のヘッダーを設定：
   - A列: ID
   - B列: 名前
   - C列: 出席
   - D列: コメント
   - E列: 更新日時
3. サービスアカウントのメールアドレスと共有（編集者権限）
4. スプレッドシートIDをコピー

### 3. ローカルで実行する場合

1. リポジトリをクローン
```bash
git clone <your-repo-url>
cd <your-repo-name>
```

2. 必要なパッケージをインストール
```bash
pip install -r requirements.txt
```

3. `.streamlit/secrets.toml`ファイルを作成
```bash
mkdir -p .streamlit
cp .streamlit/secrets.toml.example .streamlit/secrets.toml
```

4. `secrets.toml`を編集して、以下を設定：
   - スプレッドシートID
   - サービスアカウントの認証情報（ダウンロードしたJSONファイルの内容）

5. アプリを起動
```bash
streamlit run app.py
```

### 4. Streamlit Cloudにデプロイする場合

1. GitHubにリポジトリをプッシュ
2. [Streamlit Cloud](https://streamlit.io/cloud)にアクセス
3. "New app"をクリック
4. リポジトリを選択
5. "Advanced settings"で secrets を設定：
   - `spreadsheet_id`: あなたのスプレッドシートID
   - `gcp_service_account`: サービスアカウントのJSON内容をそのまま貼り付け
6. "Deploy"をクリック

## 使い方

1. **新規参加者追加**: サイドバーから名前を入力して追加
2. **出席管理**: チェックボックスをクリックして出席/欠席を記録
3. **コメント入力**: 各参加者の行にコメントを入力
4. **最新データ取得**: サイドバーの「最新データを取得」ボタンで他の人の変更を反映

## 注意事項

- `.streamlit/secrets.toml`ファイルは絶対にGitにコミットしないでください
- サービスアカウントのJSONキーは安全に管理してください
- 複数人で同時編集する場合は、定期的に「最新データを取得」ボタンを押してください

## ライセンス

MIT License
