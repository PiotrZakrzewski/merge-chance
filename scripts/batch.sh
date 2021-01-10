# pass a file with one org/repo per line (in a format as the get_pr_gql.py expects)
cat $1 | tr '\n' '\0' | xargs -0 -n1 python get_pr_gql.py
CSV_DIR="$1_prs"
OUTSIDERS_DIR="$1_prs_outsiders"
ALL_DIR="$1_prs_all"
mkdir -p $CSV_DIR
mkdir -p $OUTSIDERS_DIR
mkdir -p $ALL_DIR
mv *csv "$CSV_DIR"/
for f in $(ls $CSV_DIR)
do
  python score.py $CSV_DIR/$f  --outsiders
  mv *png "$OUTSIDERS_DIR/"
  python score.py "$CSV_DIR/$f"
  mv *png "$ALL_DIR/"
done
