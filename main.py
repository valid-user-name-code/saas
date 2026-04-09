import argparse
from pathlib import Path

import pandas as pd
from sklearn.preprocessing import OneHotEncoder
import xgboost as xgb


HERE = Path(__file__).resolve().parent
DEFAULT_TRAIN = HERE.parent / 'question' / 'data' / 'train.csv'

CATEGORICAL = ['industry', 'company_size', 'region', 'plan_tier',
                'referral_source', 'billing_status']
DROP = ['customer_id', 'snapshot_month', 'signup_date',
        'csm_touch_count_30d', 'health_score']
LABEL = 'renewed_next_month'
UNIT_DRIFT_CUTOFF = '2024-01-01'


def normalize_payment_days(df):
    df = df.copy()
    is_old = pd.to_datetime(df['snapshot_month']) < pd.Timestamp(UNIT_DRIFT_CUTOFF)
    df.loc[is_old, 'days_since_last_payment'] = df.loc[is_old, 'days_since_last_payment'] + 15
    return df


def featurize(df, encoder=None):
    df = normalize_payment_days(df)
    for col in DROP:
        if col in df.columns:
            df = df.drop(columns=col)

    cats = df[CATEGORICAL].fillna('UNK').astype(str)
    if encoder is None:
        encoder = OneHotEncoder(handle_unknown='ignore', sparse_output=False)
        encoder.fit(cats)
    cat_arr = encoder.transform(cats)

    num = df.drop(columns=CATEGORICAL).fillna(-1)
    return pd.concat([num.reset_index(drop=True),
                      pd.DataFrame(cat_arr, index=num.index)], axis=1), encoder


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--input', required=True)
    parser.add_argument('--output', required=True)
    parser.add_argument('--train', default=str(DEFAULT_TRAIN))
    args = parser.parse_args()

    train = pd.read_csv(args.train)
    y = train[LABEL].values
    X, enc = featurize(train.drop(columns=[LABEL]))

    model = xgb.XGBClassifier(
        n_estimators=400, max_depth=6, learning_rate=0.05,
        subsample=0.9, colsample_bytree=0.8,
        eval_metric='auc', random_state=0,
    )
    model.fit(X, y)

    test = pd.read_csv(args.input)
    Xt, _ = featurize(test, enc)
    Xt.columns = X.columns
    pred = model.predict_proba(Xt)[:, 1]

    pd.DataFrame({'row_id': range(len(test)), 'pred_prob': pred}).to_csv(args.output, index=False)


if __name__ == '__main__':
    main()
