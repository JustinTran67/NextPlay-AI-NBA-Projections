import os
import sys
import django
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, r2_score
import joblib

# Add backend directory to path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)

# Django setup
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project.settings')  # adjust if your project name differs
django.setup()

from backendApp.models import PlayerGameStat
from ml_models.data_preperation import add_recent_average_features


def train_and_save_model():
    """
    Fetches PlayerGameStat data from Django ORM, retrains RandomForestRegressor,
    saves model to ml_models/player_multioutput_projection.pkl, and returns path.
    """
    print("Fetching data from Django ORM")
    qs = PlayerGameStat.objects.all().values(
        'player_id',
        'game_date',
        'opponent',
        'home',
        'minutes',
        'points',
        'assists',
        'blocks',
        'steals',
        'fg_percent',
        'threepa',
        'threep',
        'threep_percent',
        'fta',
        'ft',
        'ft_percent',
        'total_rebounds',
        'personal_fouls',
        'turnovers'
    )
    df = pd.DataFrame(list(qs))
    if df.empty:
        print("⚠️ No data found in PlayerGameStat — skipping training.")
        return None

    print("Preprocessing data")
    df = add_recent_average_features(df)

    df['opponent'] = df['opponent'].fillna('Unknown')
    df['opponent'] = df['opponent'].astype('category')
    df['opponent'] = df['opponent'].cat.codes

    X = df[['player_id', 'rest_days', 'opponent', 'home', 'avg_minutes_last5', 'avg_points_last5',
            'avg_assists_last5', 'avg_blocks_last5', 'avg_steals_last5', 'avg_fg_percent_last5',
            'avg_threepa_last5', 'avg_threep_last5', 'avg_threep_percent_last5', 'avg_fta_last5',
            'avg_ft_last5', 'avg_ft_percent_last5', 'avg_total_rebounds_last5', 'avg_personal_fouls_last5',
            'avg_turnovers_last5', 'avg_did_play_last10']]

    y = df[['minutes', 'points', 'assists', 'blocks', 'steals', 'fg_percent',
            'threepa', 'threep', 'threep_percent', 'fta', 'ft', 'ft_percent',
            'total_rebounds', 'personal_fouls', 'turnovers']]

    print("🤖 Training model...")
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    model = RandomForestRegressor(n_estimators=200, random_state=42, n_jobs=-1)
    model.fit(X_train, y_train)

    y_preds = model.predict(X_test)
    print('R^2:', r2_score(y_test, y_preds, multioutput='uniform_average'))
    print('MAE:', mean_absolute_error(y_test, y_preds))

    model_path = os.path.join(BASE_DIR, 'ml_models', 'player_multioutput_projection.pkl')
    joblib.dump(model, model_path)
    print(f" Model trained and saved to {model_path}")

    return model_path


if __name__ == "__main__":
    train_and_save_model()