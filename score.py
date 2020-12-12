import sys
import os
import pandas as pd
import seaborn as sns

STALE_THRESHOLD = 90 * 24 * 60 * 60  # 90 days in seconds
if len(sys.argv) < 2:
    print("Path to a csv required as the first argument")
    sys.exit(1)
path = sys.argv[1]
data = pd.read_csv(path)


def is_stale(created, extracted):
    return (extracted - created) > STALE_THRESHOLD


def classify_pr(pr_stats):
    if pr_stats["merged"] and pr_stats["state"] == "closed":
        return "Successful"
    elif not pr_stats["merged"] and pr_stats["state"] == "closed":
        return "Rejected"
    elif pr_stats["state"] == "open" and is_stale(
        pr_stats["created_at"], pr_stats["extracted_at"]
    ):
        return "Stale"
    else:
        return "Active"


pr_class = data.apply(classify_pr, axis=1)
data = data.assign(PR=pr_class)
plot = sns.countplot(data=data, x="PR").get_figure()

repo_name = os.path.basename(path)
if repo_name.endswith(".csv"):
    repo_name = repo_name[:-4]
plot.savefig(f"{repo_name}.png")
