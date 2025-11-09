#!/usr/bin/env python3
"""
Post-processing script to fix marketing data quality issues that datagen can't handle natively.

Fixes:
1. Companies: is_customer=False should have NULL signed_date and mrr_usd=0
2. Campaign names: Ensure uniqueness
3. Temporal constraints: Child timestamps after parent creation
4. Email/Newsletter funnels: clicked=True requires opened=True
5. Social engagement: Use real person_ids instead of random
6. Transactions: Align company_id with person's company
7. Support tickets: resolved_at after created_at
"""

import pandas as pd
import numpy as np
from pathlib import Path
import sys

def fix_companies(df):
    """Fix is_customer logic"""
    print(f"  Before: {(~df['is_customer'] & df['signed_date'].notna()).sum()} non-customers with signed_date")
    print(f"  Before: {(~df['is_customer'] & (df['mrr_usd'] > 0)).sum()} non-customers with MRR")

    # Non-customers should have NULL signed_date and 0 MRR
    df.loc[~df['is_customer'], 'signed_date'] = pd.NaT
    df.loc[~df['is_customer'], 'mrr_usd'] = 0

    print(f"  After: {(~df['is_customer'] & df['signed_date'].notna()).sum()} non-customers with signed_date")
    print(f"  After: {(~df['is_customer'] & (df['mrr_usd'] > 0)).sum()} non-customers with MRR")
    return df

def fix_campaign_names(df):
    """Ensure campaign names are unique"""
    duplicates = df['campaign_name'].duplicated()
    print(f"  Before: {duplicates.sum()} duplicate campaign names")

    # Add suffix to duplicates
    counts = {}
    for idx, name in enumerate(df['campaign_name']):
        if name in counts:
            counts[name] += 1
            df.at[idx, 'campaign_name'] = f"{name} v{counts[name]}"
        else:
            counts[name] = 1

    duplicates_after = df['campaign_name'].duplicated()
    print(f"  After: {duplicates_after.sum()} duplicate campaign names")
    return df

def fix_temporal_constraints(people_df, companies_df, campaigns_df,
                            sessions_df, mentions_df, transactions_df,
                            social_posts_df, social_engagement_df, support_df):
    """Fix timeline violations"""
    fixes = []

    # 1. User sessions after person registration
    sessions_people = sessions_df.merge(people_df[['person_id', 'first_seen_date']], on='person_id')
    violations = (sessions_people['timestamp'] < sessions_people['first_seen_date']).sum()
    print(f"  Sessions before person registration: {violations}")
    if violations > 0:
        # Move session timestamp to after first_seen_date
        mask = sessions_df['timestamp'] < sessions_people['first_seen_date']
        sessions_df.loc[mask, 'timestamp'] = sessions_people.loc[mask, 'first_seen_date'] + pd.Timedelta(hours=np.random.randint(1, 24))
        fixes.append(f"Fixed {violations} sessions")

    # 2. Campaign mentions after campaign start
    mentions_campaigns = mentions_df.merge(campaigns_df[['campaign_id', 'start_date']], on='campaign_id')
    violations = (mentions_campaigns['timestamp'] < mentions_campaigns['start_date']).sum()
    print(f"  Mentions before campaign start: {violations}")
    if violations > 0:
        mask = mentions_df['timestamp'] < mentions_campaigns['start_date']
        mentions_df.loc[mask, 'timestamp'] = mentions_campaigns.loc[mask, 'start_date'] + pd.Timedelta(days=np.random.randint(1, 30))
        fixes.append(f"Fixed {violations} mentions")

    # 3. Transactions after company signed
    transactions_companies = transactions_df.merge(companies_df[['company_id', 'signed_date']], on='company_id')
    violations = (transactions_companies['timestamp'] < transactions_companies['signed_date']).sum()
    print(f"  Transactions before company signed: {violations}")
    if violations > 0:
        mask = transactions_df['timestamp'] < transactions_companies['signed_date']
        transactions_df.loc[mask, 'timestamp'] = transactions_companies.loc[mask, 'signed_date'] + pd.Timedelta(days=np.random.randint(1, 90))
        fixes.append(f"Fixed {violations} transactions")

    # 4. Social engagement after posts
    engagement_posts = social_engagement_df.merge(social_posts_df[['post_id', 'posted_at']], on='post_id')
    violations = (engagement_posts['timestamp'] < engagement_posts['posted_at']).sum()
    print(f"  Engagement before posts: {violations}")
    if violations > 0:
        mask = social_engagement_df['timestamp'] < engagement_posts['posted_at']
        social_engagement_df.loc[mask, 'timestamp'] = engagement_posts.loc[mask, 'posted_at'] + pd.Timedelta(minutes=np.random.randint(1, 1440))
        fixes.append(f"Fixed {violations} engagements")

    # 5. Support tickets: resolved_at after created_at
    violations = (support_df['resolved_at'] < support_df['created_at']).sum()
    print(f"  Tickets resolved before created: {violations}")
    if violations > 0:
        mask = support_df['resolved_at'] < support_df['created_at']
        support_df.loc[mask, 'resolved_at'] = support_df.loc[mask, 'created_at'] + pd.Timedelta(hours=np.random.randint(1, 72))
        fixes.append(f"Fixed {violations} support tickets")

    return fixes

def fix_email_funnels(email_df, newsletter_df):
    """Fix impossible funnel states"""
    fixes = []

    # Email: clicked=True requires opened=True
    violations = (email_df['clicked'] & ~email_df['opened']).sum()
    print(f"  Emails clicked without opening: {violations}")
    if violations > 0:
        email_df.loc[email_df['clicked'] & ~email_df['opened'], 'opened'] = True
        fixes.append(f"Fixed {violations} email records")

    # Email: converted=True requires opened=True
    violations = (email_df['converted'] & ~email_df['opened']).sum()
    if violations > 0:
        email_df.loc[email_df['converted'] & ~email_df['opened'], 'opened'] = True
        fixes.append(f"Fixed {violations} email conversions")

    # Newsletter: clicked=True requires opened=True
    violations = (newsletter_df['clicked'] & ~newsletter_df['opened']).sum()
    print(f"  Newsletters clicked without opening: {violations}")
    if violations > 0:
        newsletter_df.loc[newsletter_df['clicked'] & ~newsletter_df['opened'], 'opened'] = True
        fixes.append(f"Fixed {violations} newsletter records")

    return fixes

def fix_social_engagement_users(engagement_df, people_df):
    """Replace random user_ids with real person_ids"""
    print(f"  Distinct user_ids before: {engagement_df['user_id'].nunique()}")

    # Sample from people table
    person_ids = people_df['person_id'].values
    engagement_df['user_id'] = np.random.choice(person_ids, size=len(engagement_df))

    print(f"  Distinct user_ids after: {engagement_df['user_id'].nunique()}")
    return engagement_df

def fix_transaction_company_alignment(transactions_df, people_df):
    """Ensure transaction company_id matches person's company_id"""
    transactions_people = transactions_df.merge(people_df[['person_id', 'company_id']],
                                                 on='person_id', suffixes=('', '_person'))
    violations = (transactions_df['company_id'] != transactions_people['company_id_person']).sum()
    print(f"  Transactions with mismatched company: {violations}")

    if violations > 0:
        # Update company_id to match person's company
        transactions_df['company_id'] = transactions_people['company_id_person']

    return transactions_df

def main():
    data_dir = Path(sys.argv[1]) if len(sys.argv) > 1 else Path('/tmp/datagen/marketing_example')

    print("=" * 80)
    print("MARKETING DATA POST-PROCESSING")
    print("=" * 80)

    # Load all tables
    print("\nLoading data...")
    companies = pd.read_csv(data_dir / 'companies.csv')
    campaigns = pd.read_csv(data_dir / 'campaigns.csv')
    people = pd.read_csv(data_dir / 'people.csv', parse_dates=['first_seen_date'])
    user_sessions = pd.read_csv(data_dir / 'user_sessions.csv', parse_dates=['timestamp'])
    campaign_mentions = pd.read_csv(data_dir / 'campaign_mentions.csv', parse_dates=['timestamp'])
    transactions = pd.read_csv(data_dir / 'transactions.csv', parse_dates=['timestamp'])
    email_sends = pd.read_csv(data_dir / 'email_sends.csv', parse_dates=['sent_at'])
    newsletter_sends = pd.read_csv(data_dir / 'newsletter_sends.csv', parse_dates=['sent_at'])
    social_posts = pd.read_csv(data_dir / 'social_posts.csv', parse_dates=['posted_at'])
    social_engagement = pd.read_csv(data_dir / 'social_engagement.csv', parse_dates=['timestamp'])
    support_tickets = pd.read_csv(data_dir / 'support_tickets.csv', parse_dates=['created_at', 'resolved_at'])

    # Parse dates where needed
    companies['signed_date'] = pd.to_datetime(companies['signed_date'], errors='coerce')
    campaigns['start_date'] = pd.to_datetime(campaigns['start_date'])

    # Apply fixes
    print("\n1. Fixing companies is_customer logic...")
    companies = fix_companies(companies)

    print("\n2. Fixing campaign name uniqueness...")
    campaigns = fix_campaign_names(campaigns)

    print("\n3. Fixing temporal constraints...")
    temporal_fixes = fix_temporal_constraints(
        people, companies, campaigns,
        user_sessions, campaign_mentions, transactions,
        social_posts, social_engagement, support_tickets
    )

    print("\n4. Fixing email/newsletter funnels...")
    funnel_fixes = fix_email_funnels(email_sends, newsletter_sends)

    print("\n5. Fixing social engagement user_ids...")
    social_engagement = fix_social_engagement_users(social_engagement, people)

    print("\n6. Fixing transaction-company alignment...")
    transactions = fix_transaction_company_alignment(transactions, people)

    # Save fixed data
    print("\n7. Saving fixed data...")
    companies.to_csv(data_dir / 'companies.csv', index=False)
    campaigns.to_csv(data_dir / 'campaigns.csv', index=False)
    user_sessions.to_csv(data_dir / 'user_sessions.csv', index=False)
    campaign_mentions.to_csv(data_dir / 'campaign_mentions.csv', index=False)
    transactions.to_csv(data_dir / 'transactions.csv', index=False)
    email_sends.to_csv(data_dir / 'email_sends.csv', index=False)
    newsletter_sends.to_csv(data_dir / 'newsletter_sends.csv', index=False)
    social_engagement.to_csv(data_dir / 'social_engagement.csv', index=False)
    support_tickets.to_csv(data_dir / 'support_tickets.csv', index=False)

    print("\n" + "=" * 80)
    print("POST-PROCESSING COMPLETE")
    print("=" * 80)
    print(f"\nAll fixes applied: {len(temporal_fixes) + len(funnel_fixes) + 4} categories")
    print("\nFixed tables saved to:", data_dir)

if __name__ == '__main__':
    main()
