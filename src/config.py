from dataclasses import dataclass

@dataclass
class Config:
    token: str = 'BOT_TOKEN'
    admin_ids: int = 'ADMIN_IDS'
    pay_token: str = 'PAYMENT_TOKEN'
    token_p2p: str = 'P2P_TOKEN'
