from huggingface_hub import hf_hub_download


def download_classifier(net_name, target, train_version, net_type = "cnn", use_our_models = False):
    if use_our_models:
        return hf_hub_download(
            repo_id="M1PISEN/MESCnn_finetuned",
            filename=f"classification/logs/cnn/holdout/{net_name}_{target}_{train_version}_fine_tuned.pth",
            token="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",
            local_dir='./mescnn',
            local_dir_use_symlinks=False,
            force_download=True,
        )
    else :
        return hf_hub_download(
            repo_id="MESCnn/MESCnn",
            filename=f"classification/logs/cnn/holdout/{net_name}_{target}_{train_version}.pth",
            token="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",
            local_dir='./mescnn',
            local_dir_use_symlinks=False,
            force_download=True,
        )
