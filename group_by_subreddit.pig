A = LOAD 'user_subreddit_tuples.csv' USING PigStorage(',') AS (user:chararray,subreddit:chararray);
B = GROUP A by subreddit;
C = FOREACH B {
  D = DISTINCT A.$0;
  GENERATE group, D;
}
STORE C INTO 'groups';