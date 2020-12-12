from github import Github
import os
import sys


token = os.getenv("GH_TOKEN")
if not token:
    print("You need to set GH_TOKEN env var")
    sys.exit(1)
if len(sys.argv) < 2:
    print("Pass github repo name as first position argument.\n 'facebook/react' for example")
    sys.exit(1)

g = Github(token)
target_repo_id = sys.argv[1]
target_repo = g.get_repo(target_repo_id)
csv_data = [[ "state", "created_at", "merged", "merge_date", "no_comments"]]

results = target_repo.get_pulls()
total = results.totalCount
processed_prs = 0
print(f"{total} open PRs to process...")
for pr in results:
    created_at = pr.created_at.timestamp() if pr.created_at else "N/A"
    merged_at = pr.merged_at.timestamp() if pr.merged_at else "N/A"
    row = [ pr.state,
           f"{created_at}",
           f"{pr.merged}", 
           f"{merged_at}", 
           f"{pr.comments}"]
    csv_data.append(row)
    processed_prs += 1
    if (processed_prs % 100) == 0:
        perc_progress = round(processed_prs/total * 100, 2)
        print(f"Processed {perc_progress} % of PRs")

results = target_repo.get_pulls(state="closed")
total = results.totalCount
processed_prs = 0
print(f"{total} closed PRs to process...")
for pr in results:
    created_at = pr.created_at.timestamp() if pr.created_at else "N/A"
    merged_at = pr.merged_at.timestamp() if pr.merged_at else "N/A"
    row = [ pr.state,
           f"{created_at}",
           f"{pr.merged}", 
           f"{merged_at}", 
           f"{pr.comments}"]
    csv_data.append(row)
    processed_prs += 1
    if (processed_prs % 100) == 0:
        perc_progress = round(processed_prs/total * 100, 2)
        print(f"Processed {perc_progress} % of PRs")
csv_name = f"{target_repo_id}.csv"
csv_name = csv_name.replace(os.sep, "_")
print(f"Will write results to {csv_name}")
with open(csv_name, "w") as outfile:
    lines = [",".join(row) for row in csv_data]
    text = "\n".join(lines)
    outfile.write(text)
