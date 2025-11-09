#!/usr/bin/env python3
"""Fix remaining temporal issue with transactions"""

import pandas as pd
import numpy as np

data_dir = '/tmp/datagen/marketing_example'

print("Fixing remaining transaction timeline issue...")

companies = pd.read_csv(f'{data_dir}/companies.csv', parse_dates=['signed_date'])
transactions = pd.read_csv(f'{data_dir}/transactions.csv', parse_dates=['timestamp'])

# Merge to get signed dates
trans_companies = transactions.merge(companies[['company_id', 'signed_date', 'is_customer']], on='company_id')

# For transactions where signed_date is NULL (non-customers), use transaction timestamp
# For others, ensure transaction is after signed_date
violations_before = (trans_companies['timestamp'] < trans_companies['signed_date']).sum()
print(f"Before: {violations_before} transactions before company signed")

# Fix: Move transactions to after signed_date
mask = trans_companies['timestamp'] < trans_companies['signed_date']
if mask.sum() > 0:
    # Add random days after signed_date
    signed_dates = trans_companies.loc[mask, 'signed_date']
    days_after = np.random.randint(1, 90, size=mask.sum())
    transactions.loc[mask, 'timestamp'] = signed_dates + pd.to_timedelta(days_after, unit='D')

# Save
transactions.to_csv(f'{data_dir}/transactions.csv', index=False)

# Verify
trans_companies = transactions.merge(companies[['company_id', 'signed_date']], on='company_id')
violations_after = (trans_companies['timestamp'] < trans_companies['signed_date']).sum()
print(f"After: {violations_after} transactions before company signed")
print("✓ Fix complete!")
