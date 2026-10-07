from huggingface_hub import snapshot_download

path = snapshot_download(
    repo_id="allenai/WildChat-4.8M",
    repo_type="dataset",
    local_dir="wildchat_4_8m",
)
print(f"Selesai, data tersimpan di: {path}")