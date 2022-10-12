from yoomoney import Authorize

Authorize(
      client_id="36DC67D8360C966622329EAD5B4A9E2ACE47DB7E10902B35F435B226C3BBE55A",
      redirect_uri="https://t.me/teg_test_idea_bot",
      scope=["account-info",
             "operation-history",
             "operation-details",
             "incoming-transfers",
             "payment-p2p",
             "payment-shop",
             ]
      )

