from dataclasses import dataclass

from dotenv import dotenv_values


@dataclass
class Config:
    obs_host: str = "localhost"
    obs_port: int = 4444
    obs_password: str = "secret"
    text_path: str = "/tmp"  # nosec

    def __post_init__(self):
        dotenv_config = dotenv_values()
        fields = vars(self)
        for k, v in fields.items():
            new_v = dotenv_config.get(k, v)
            setattr(self, k, new_v)


config = Config()
