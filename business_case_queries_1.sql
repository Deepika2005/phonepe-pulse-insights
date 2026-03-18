-- ═══════════════════════════════════════════════════════════════════════════
--  PhonePe Pulse — SQL Business Case Studies
--  Database : phonepe_pulse
--  Column Standards (Colab) :
--    aggregated_transaction → State, Year, Quater, Transacion_type,
--                              Transacion_count, Transacion_amount
--    aggregated_user        → State, Year, Quater, Brands, Count,
--                              Percentage, Registered_user, App_opens
--    aggregated_insurance   → State, Year, Quater, Transacion_type,
--                              Transacion_count, Transacion_amount
--    map_transaction        → State, Year, Quater, District, Count, Amount
--    map_user               → State, Year, Quater, District,
--                              Registered_user, App_opens
--    top_transaction        → State, Year, Quater, EntityType,
--                              EntityName, Count, Amount
--    top_user               → State, Year, Quater, EntityType,
--                              EntityName, Registered_user
-- ═══════════════════════════════════════════════════════════════════════════

USE phonepe_pulse;


-- ███████████████████████████████████████████████████████████████████████████
--
--  CASE STUDY 1 : DECODING TRANSACTION DYNAMICS ON PHONEPE
--  Goal : Understand variation in transaction behavior across states,
--         quarters, and payment categories to drive targeted strategies.
--
-- ███████████████████████████████████████████████████████████████████████████

-- ── Q1.1  Overall transaction summary (count + amount + avg) ─────────────────
SELECT
    SUM(Transacion_count)                          AS Total_Transactions,
    ROUND(SUM(Transacion_amount), 2)               AS Total_Amount,
    ROUND(SUM(Transacion_amount)
          / SUM(Transacion_count), 2)              AS Avg_Transaction_Value
FROM aggregated_transaction;


-- ── Q1.2  Year-wise transaction growth ───────────────────────────────────────
SELECT
    Year,
    SUM(Transacion_count)              AS Total_Transactions,
    ROUND(SUM(Transacion_amount), 2)   AS Total_Amount,
    ROUND(
        (SUM(Transacion_amount) - LAG(SUM(Transacion_amount))
            OVER (ORDER BY Year))
        / LAG(SUM(Transacion_amount))
            OVER (ORDER BY Year) * 100, 2
    )                                  AS YoY_Growth_Pct
FROM aggregated_transaction
GROUP BY Year
ORDER BY Year;


-- ── Q1.3  Quarter-wise transaction trend ─────────────────────────────────────
SELECT
    Year,
    Quater,
    SUM(Transacion_count)             AS Total_Transactions,
    ROUND(SUM(Transacion_amount), 2)  AS Total_Amount
FROM aggregated_transaction
GROUP BY Year, Quater
ORDER BY Year, Quater;


-- ── Q1.4  Transaction breakdown by payment category ──────────────────────────
SELECT
    Transacion_type,
    SUM(Transacion_count)                                    AS Total_Count,
    ROUND(SUM(Transacion_amount), 2)                         AS Total_Amount,
    ROUND(SUM(Transacion_count) * 100.0
          / SUM(SUM(Transacion_count)) OVER (), 2)           AS Count_Share_Pct,
    ROUND(SUM(Transacion_amount) * 100.0
          / SUM(SUM(Transacion_amount)) OVER (), 2)          AS Amount_Share_Pct
FROM aggregated_transaction
GROUP BY Transacion_type
ORDER BY Total_Amount DESC;


-- ── Q1.5  Top 10 states by total transaction amount ──────────────────────────
SELECT
    State,
    SUM(Transacion_count)             AS Total_Transactions,
    ROUND(SUM(Transacion_amount), 2)  AS Total_Amount,
    ROUND(AVG(Transacion_amount), 2)  AS Avg_Amount
FROM aggregated_transaction
GROUP BY State
ORDER BY Total_Amount DESC
LIMIT 10;


-- ── Q1.6  Bottom 10 states (stagnation/low adoption) ─────────────────────────
SELECT
    State,
    SUM(Transacion_count)             AS Total_Transactions,
    ROUND(SUM(Transacion_amount), 2)  AS Total_Amount
FROM aggregated_transaction
GROUP BY State
ORDER BY Total_Amount ASC
LIMIT 10;


-- ── Q1.7  State × Quarter — peak transaction periods ─────────────────────────
SELECT
    State,
    Year,
    Quater,
    SUM(Transacion_count)             AS Total_Transactions,
    ROUND(SUM(Transacion_amount), 2)  AS Total_Amount,
    RANK() OVER (
        PARTITION BY State
        ORDER BY SUM(Transacion_amount) DESC
    )                                 AS Rank_Within_State
FROM aggregated_transaction
GROUP BY State, Year, Quater
ORDER BY State, Rank_Within_State;


-- ── Q1.8  Most popular payment type per state ────────────────────────────────
SELECT
    State,
    Transacion_type,
    SUM(Transacion_count)  AS Total_Count
FROM aggregated_transaction
GROUP BY State, Transacion_type
HAVING SUM(Transacion_count) = (
    SELECT MAX(inner_sum)
    FROM (
        SELECT SUM(Transacion_count) AS inner_sum
        FROM aggregated_transaction t2
        WHERE t2.State = aggregated_transaction.State
        GROUP BY t2.Transacion_type
    ) sub
)
ORDER BY Total_Count DESC;


-- ── Q1.9  States with declining transactions (YoY drop) ──────────────────────
WITH yearly AS (
    SELECT
        State, Year,
        SUM(Transacion_amount) AS Yearly_Amount
    FROM aggregated_transaction
    GROUP BY State, Year
)
SELECT
    curr.State,
    curr.Year                             AS Current_Year,
    ROUND(curr.Yearly_Amount, 2)          AS Current_Amount,
    ROUND(prev.Yearly_Amount, 2)          AS Previous_Amount,
    ROUND((curr.Yearly_Amount - prev.Yearly_Amount)
          / prev.Yearly_Amount * 100, 2)  AS Growth_Pct
FROM yearly curr
JOIN yearly prev
    ON curr.State = prev.State
    AND curr.Year = prev.Year + 1
WHERE curr.Yearly_Amount < prev.Yearly_Amount
ORDER BY Growth_Pct ASC;


-- ██████████████████████████████████████████████████████████████████████████
--
--  CASE STUDY 2 : DEVICE DOMINANCE AND USER ENGAGEMENT ANALYSIS
--  Goal : Understand user preferences across device brands, regions,
--         and time periods. Identify underutilised devices.
--
-- ██████████████████████████████████████████████████████████████████████████

-- ── Q2.1  Overall registered users and app opens ─────────────────────────────
SELECT
    SUM(Registered_user)   AS Total_Registered_Users,
    SUM(App_opens)         AS Total_App_Opens,
    ROUND(SUM(App_opens)
          / SUM(Registered_user), 2)   AS Avg_Opens_Per_User
FROM aggregated_user;


-- ── Q2.2  Top 10 mobile brands by user count ─────────────────────────────────
SELECT
    Brands,
    SUM(Count)                                          AS Total_Users,
    ROUND(AVG(Percentage) * 100, 2)                     AS Avg_Market_Share_Pct,
    ROUND(SUM(Count) * 100.0
          / SUM(SUM(Count)) OVER (), 2)                 AS Overall_Share_Pct
FROM aggregated_user
WHERE Brands IS NOT NULL
GROUP BY Brands
ORDER BY Total_Users DESC
LIMIT 10;


-- ── Q2.3  Top 10 states by registered users ──────────────────────────────────
SELECT
    State,
    SUM(Registered_user)   AS Total_Registered,
    SUM(App_opens)         AS Total_App_Opens,
    ROUND(SUM(App_opens)
          / SUM(Registered_user), 2)  AS Engagement_Ratio
FROM aggregated_user
GROUP BY State
ORDER BY Total_Registered DESC
LIMIT 10;


-- ── Q2.4  States with HIGH registrations but LOW engagement (underutilised) ───
SELECT
    State,
    SUM(Registered_user)                              AS Total_Registered,
    SUM(App_opens)                                    AS Total_App_Opens,
    ROUND(SUM(App_opens) / SUM(Registered_user), 2)  AS Engagement_Ratio
FROM aggregated_user
GROUP BY State
HAVING Engagement_Ratio < (
    SELECT ROUND(AVG(App_opens / Registered_user), 2)
    FROM aggregated_user
    WHERE Registered_user > 0
)
ORDER BY Total_Registered DESC
LIMIT 10;


-- ── Q2.5  Brand dominance per state (top brand per state) ────────────────────
WITH brand_rank AS (
    SELECT
        State, Brands,
        SUM(Count)  AS Brand_Users,
        RANK() OVER (PARTITION BY State ORDER BY SUM(Count) DESC) AS rnk
    FROM aggregated_user
    WHERE Brands IS NOT NULL
    GROUP BY State, Brands
)
SELECT
    State,
    Brands  AS Top_Brand,
    Brand_Users
FROM brand_rank
WHERE rnk = 1
ORDER BY Brand_Users DESC;


-- ── Q2.6  Year-wise user growth ───────────────────────────────────────────────
SELECT
    Year,
    SUM(Registered_user)   AS Total_Registered,
    SUM(App_opens)         AS Total_App_Opens,
    ROUND(SUM(App_opens)
          / SUM(Registered_user), 2)  AS Engagement_Ratio
FROM aggregated_user
GROUP BY Year
ORDER BY Year;


-- ── Q2.7  Quarter-wise user engagement trend ─────────────────────────────────
SELECT
    Year,
    Quater,
    SUM(Registered_user)  AS Total_Registered,
    SUM(App_opens)        AS Total_App_Opens,
    ROUND(SUM(App_opens)
          / SUM(Registered_user), 2)  AS Engagement_Ratio
FROM aggregated_user
GROUP BY Year, Quater
ORDER BY Year, Quater;


-- ── Q2.8  Top 10 districts by registered users ───────────────────────────────
SELECT
    District,
    State,
    SUM(Registered_user)   AS Total_Registered,
    SUM(App_opens)         AS Total_App_Opens
FROM map_user
GROUP BY District, State
ORDER BY Total_Registered DESC
LIMIT 10;


-- ── Q2.9  Brand growth over years ────────────────────────────────────────────
SELECT
    Brands,
    Year,
    SUM(Count)                AS Yearly_Users,
    ROUND(
        (SUM(Count) - LAG(SUM(Count)) OVER (PARTITION BY Brands ORDER BY Year))
        / LAG(SUM(Count)) OVER (PARTITION BY Brands ORDER BY Year) * 100
    , 2)                      AS YoY_Growth_Pct
FROM aggregated_user
WHERE Brands IS NOT NULL
GROUP BY Brands, Year
ORDER BY Brands, Year;


-- ██████████████████████████████████████████████████████████████████████████
--
--  CASE STUDY 3 : INSURANCE PENETRATION AND GROWTH POTENTIAL
--  Goal : Analyze insurance growth trajectory and identify untapped
--         opportunities for adoption at state level.
--
-- ██████████████████████████████████████████████████████████████████████████

-- ── Q3.1  Overall insurance transaction summary ──────────────────────────────
SELECT
    SUM(Transacion_count)              AS Total_Policies,
    ROUND(SUM(Transacion_amount), 2)   AS Total_Premium_Amount,
    ROUND(AVG(Transacion_amount), 2)   AS Avg_Premium_Value
FROM aggregated_insurance;


-- ── Q3.2  Year-wise insurance growth ─────────────────────────────────────────
SELECT
    Year,
    SUM(Transacion_count)              AS Total_Policies,
    ROUND(SUM(Transacion_amount), 2)   AS Total_Amount,
    ROUND(
        (SUM(Transacion_amount) - LAG(SUM(Transacion_amount))
            OVER (ORDER BY Year))
        / LAG(SUM(Transacion_amount))
            OVER (ORDER BY Year) * 100
    , 2)                               AS YoY_Growth_Pct
FROM aggregated_insurance
GROUP BY Year
ORDER BY Year;


-- ── Q3.3  Top 10 states by insurance amount ──────────────────────────────────
SELECT
    State,
    SUM(Transacion_count)              AS Total_Policies,
    ROUND(SUM(Transacion_amount), 2)   AS Total_Amount,
    ROUND(SUM(Transacion_amount) * 100.0
          / SUM(SUM(Transacion_amount)) OVER (), 2)   AS Amount_Share_Pct
FROM aggregated_insurance
GROUP BY State
ORDER BY Total_Amount DESC
LIMIT 10;


-- ── Q3.4  States with lowest insurance penetration (untapped markets) ─────────
SELECT
    State,
    SUM(Transacion_count)              AS Total_Policies,
    ROUND(SUM(Transacion_amount), 2)   AS Total_Amount
FROM aggregated_insurance
GROUP BY State
ORDER BY Total_Policies ASC
LIMIT 10;


-- ── Q3.5  Insurance vs Transaction comparison per state ───────────────────────
SELECT
    t.State,
    SUM(t.Transacion_amount)           AS Txn_Amount,
    SUM(i.Transacion_amount)           AS Insurance_Amount,
    ROUND(SUM(i.Transacion_amount)
          / SUM(t.Transacion_amount) * 100, 4)   AS Insurance_Penetration_Pct
FROM aggregated_transaction t
JOIN aggregated_insurance   i
    ON t.State = i.State
    AND t.Year = i.Year
    AND t.Quater = i.Quater
GROUP BY t.State
ORDER BY Insurance_Penetration_Pct DESC;


-- ── Q3.6  Quarter-wise insurance growth trend ────────────────────────────────
SELECT
    Year,
    Quater,
    SUM(Transacion_count)             AS Total_Policies,
    ROUND(SUM(Transacion_amount), 2)  AS Total_Amount
FROM aggregated_insurance
GROUP BY Year, Quater
ORDER BY Year, Quater;


-- ── Q3.7  Top 10 districts by insurance amount ───────────────────────────────
SELECT
    District,
    State,
    SUM(Count)                        AS Total_Policies,
    ROUND(SUM(Amount), 2)             AS Total_Amount
FROM map_insurance
GROUP BY District, State
ORDER BY Total_Amount DESC
LIMIT 10;


-- ── Q3.8  States with fastest insurance growth (YoY) ─────────────────────────
WITH ins_yearly AS (
    SELECT State, Year,
           SUM(Transacion_amount) AS Yearly_Amount
    FROM aggregated_insurance
    GROUP BY State, Year
)
SELECT
    curr.State,
    curr.Year,
    ROUND(curr.Yearly_Amount, 2)          AS Current_Amount,
    ROUND(prev.Yearly_Amount, 2)          AS Previous_Amount,
    ROUND((curr.Yearly_Amount - prev.Yearly_Amount)
          / prev.Yearly_Amount * 100, 2)  AS Growth_Pct
FROM ins_yearly curr
JOIN ins_yearly prev
    ON curr.State = prev.State
    AND curr.Year = prev.Year + 1
ORDER BY Growth_Pct DESC
LIMIT 10;


-- ██████████████████████████████████████████████████████████████████████████
--
--  CASE STUDY 4 : TRANSACTION ANALYSIS FOR MARKET EXPANSION
--  Goal : Analyze transaction data at state level to identify trends,
--         opportunities, and potential areas for expansion.
--
-- ██████████████████████████████████████════════════════════════════════════

-- ── Q4.1  State-wise transaction summary with ranking ────────────────────────
SELECT
    State,
    SUM(Transacion_count)              AS Total_Transactions,
    ROUND(SUM(Transacion_amount), 2)   AS Total_Amount,
    ROUND(AVG(Transacion_amount), 2)   AS Avg_Amount,
    RANK() OVER (ORDER BY SUM(Transacion_amount) DESC)  AS Amount_Rank,
    RANK() OVER (ORDER BY SUM(Transacion_count)  DESC)  AS Count_Rank
FROM aggregated_transaction
GROUP BY State
ORDER BY Amount_Rank;


-- ── Q4.2  High volume + low value states (expansion opportunity) ──────────────
SELECT
    State,
    SUM(Transacion_count)                                    AS Total_Count,
    ROUND(SUM(Transacion_amount), 2)                         AS Total_Amount,
    ROUND(SUM(Transacion_amount) / SUM(Transacion_count), 2) AS Avg_Txn_Value
FROM aggregated_transaction
GROUP BY State
HAVING Avg_Txn_Value < (
    SELECT SUM(Transacion_amount) / SUM(Transacion_count)
    FROM aggregated_transaction
)
ORDER BY Total_Count DESC
LIMIT 10;


-- ── Q4.3  Top 5 states per transaction type ──────────────────────────────────
WITH ranked AS (
    SELECT
        State,
        Transacion_type,
        SUM(Transacion_count)   AS Total_Count,
        ROUND(SUM(Transacion_amount), 2)  AS Total_Amount,
        RANK() OVER (
            PARTITION BY Transacion_type
            ORDER BY SUM(Transacion_amount) DESC
        )  AS rnk
    FROM aggregated_transaction
    GROUP BY State, Transacion_type
)
SELECT State, Transacion_type, Total_Count, Total_Amount
FROM ranked
WHERE rnk <= 5
ORDER BY Transacion_type, Total_Amount DESC;


-- ── Q4.4  District-level top performers ──────────────────────────────────────
SELECT
    District,
    State,
    SUM(Count)                        AS Total_Transactions,
    ROUND(SUM(Amount), 2)             AS Total_Amount,
    ROUND(SUM(Amount) / SUM(Count), 2) AS Avg_Txn_Value
FROM map_transaction
GROUP BY District, State
ORDER BY Total_Amount DESC
LIMIT 15;


-- ── Q4.5  Top 10 pincodes by transaction amount ──────────────────────────────
SELECT
    EntityName  AS Pincode,
    State,
    SUM(Count)                   AS Total_Transactions,
    ROUND(SUM(Amount), 2)        AS Total_Amount
FROM top_transaction
WHERE EntityType = 'Pincode'
GROUP BY EntityName, State
ORDER BY Total_Amount DESC
LIMIT 10;


-- ── Q4.6  Emerging states — low base but high growth ─────────────────────────
WITH state_yearly AS (
    SELECT State, Year,
           SUM(Transacion_amount) AS Yearly_Amount
    FROM aggregated_transaction
    GROUP BY State, Year
),
growth AS (
    SELECT
        curr.State,
        ROUND((curr.Yearly_Amount - prev.Yearly_Amount)
              / prev.Yearly_Amount * 100, 2)  AS Growth_Pct,
        prev.Yearly_Amount                    AS Base_Amount
    FROM state_yearly curr
    JOIN state_yearly prev
        ON curr.State = prev.State
        AND curr.Year = prev.Year + 1
    WHERE prev.Year = (SELECT MIN(Year) FROM aggregated_transaction)
)
SELECT  State, Base_Amount, Growth_Pct
FROM    growth
ORDER BY Growth_Pct DESC
LIMIT 10;


-- ── Q4.7  Quarter-on-quarter transaction momentum per state ──────────────────
WITH qoq AS (
    SELECT
        State, Year, Quater,
        SUM(Transacion_amount) AS Qtr_Amount,
        LAG(SUM(Transacion_amount))
            OVER (PARTITION BY State ORDER BY Year, Quater)  AS Prev_Qtr_Amount
    FROM aggregated_transaction
    GROUP BY State, Year, Quater
)
SELECT
    State, Year, Quater,
    ROUND(Qtr_Amount, 2)     AS Current_Amount,
    ROUND(Prev_Qtr_Amount, 2) AS Previous_Amount,
    ROUND((Qtr_Amount - Prev_Qtr_Amount)
          / Prev_Qtr_Amount * 100, 2)  AS QoQ_Growth_Pct
FROM qoq
WHERE Prev_Qtr_Amount IS NOT NULL
ORDER BY QoQ_Growth_Pct DESC
LIMIT 20;


-- ██████████████████████████████████████████████████████████████████████████
--
--  CASE STUDY 5 : USER ENGAGEMENT AND GROWTH STRATEGY
--  Goal : Analyze user engagement across states and districts to provide
--         strategic insights for growth and market positioning.
--
-- ██████████████████████████████████████████████████████████████████████████

-- ── Q5.1  State-wise engagement score (app opens / registered users) ──────────
SELECT
    State,
    SUM(Registered_user)                              AS Total_Registered,
    SUM(App_opens)                                    AS Total_App_Opens,
    ROUND(SUM(App_opens) / SUM(Registered_user), 2)  AS Engagement_Score,
    CASE
        WHEN SUM(App_opens) / SUM(Registered_user) >= 50  THEN 'High'
        WHEN SUM(App_opens) / SUM(Registered_user) >= 20  THEN 'Medium'
        ELSE 'Low'
    END                                               AS Engagement_Category
FROM aggregated_user
GROUP BY State
ORDER BY Engagement_Score DESC;


-- ── Q5.2  Top 10 districts by registered users ───────────────────────────────
SELECT
    District,
    State,
    SUM(Registered_user)   AS Total_Registered,
    SUM(App_opens)         AS Total_App_Opens,
    ROUND(SUM(App_opens)
          / SUM(Registered_user), 2)   AS Engagement_Score
FROM map_user
GROUP BY District, State
ORDER BY Total_Registered DESC
LIMIT 10;


-- ── Q5.3  Low-engagement districts (high users, low opens) ───────────────────
SELECT
    District,
    State,
    SUM(Registered_user)                              AS Total_Registered,
    SUM(App_opens)                                    AS Total_App_Opens,
    ROUND(SUM(App_opens) / SUM(Registered_user), 2)  AS Engagement_Score
FROM map_user
GROUP BY District, State
HAVING Total_Registered > 10000
   AND Engagement_Score < 5
ORDER BY Total_Registered DESC
LIMIT 10;


-- ── Q5.4  Top 10 pincodes by registered users ────────────────────────────────
SELECT
    EntityName   AS Pincode,
    State,
    SUM(Registered_user)   AS Total_Registered
FROM top_user
WHERE EntityType = 'Pincode'
GROUP BY EntityName, State
ORDER BY Total_Registered DESC
LIMIT 10;


-- ── Q5.5  States with highest user growth (YoY) ──────────────────────────────
WITH user_yearly AS (
    SELECT State, Year,
           SUM(Registered_user) AS Yearly_Users
    FROM aggregated_user
    GROUP BY State, Year
)
SELECT
    curr.State,
    curr.Year,
    curr.Yearly_Users                                     AS Current_Users,
    prev.Yearly_Users                                     AS Previous_Users,
    ROUND((curr.Yearly_Users - prev.Yearly_Users)
          / prev.Yearly_Users * 100, 2)                   AS User_Growth_Pct
FROM user_yearly curr
JOIN user_yearly prev
    ON curr.State = prev.State
    AND curr.Year = prev.Year + 1
ORDER BY User_Growth_Pct DESC
LIMIT 10;


-- ── Q5.6  Correlation between transactions and user engagement per state ───────
SELECT
    t.State,
    SUM(t.Transacion_count)                           AS Total_Transactions,
    SUM(u.Registered_user)                            AS Total_Users,
    SUM(u.App_opens)                                  AS Total_App_Opens,
    ROUND(SUM(t.Transacion_count)
          / SUM(u.Registered_user), 2)                AS Txn_Per_User,
    ROUND(SUM(u.App_opens)
          / SUM(u.Registered_user), 2)                AS Opens_Per_User
FROM aggregated_transaction t
JOIN aggregated_user u
    ON t.State = t.State
    AND t.Year = u.Year
    AND t.Quater = u.Quater
GROUP BY t.State
ORDER BY Txn_Per_User DESC
LIMIT 15;


-- ── Q5.7  Quarter-wise new user acquisition trend ────────────────────────────
SELECT
    Year,
    Quater,
    SUM(Registered_user)   AS New_Registered_Users,
    SUM(App_opens)         AS Total_App_Opens
FROM aggregated_user
GROUP BY Year, Quater
ORDER BY Year, Quater;


-- ── Q5.8  Top 10 districts by App Opens ──────────────────────────────────────
SELECT
    District,
    State,
    SUM(App_opens)         AS Total_App_Opens,
    SUM(Registered_user)   AS Total_Registered,
    ROUND(SUM(App_opens)
          / SUM(Registered_user), 2)  AS Opens_Per_User
FROM map_user
GROUP BY District, State
ORDER BY Total_App_Opens DESC
LIMIT 10;


-- ═══════════════════════════════════════════════════════════════════════════
--  END OF SQL BUSINESS CASE STUDIES
-- ═══════════════════════════════════════════════════════════════════════════