class Schema:
    def __init__(self):
        self.schema = """
spending-limit sub attribute, value double;
payment-history sub attribute, value string;
interest-rate sub attribute, value double;
minimum-payment sub attribute, value double;
late-fee sub attribute, value double;
bank-name sub attribute, value string;
pro sub attribute, value string;

credit-card-user sub entity,
  owns spending-limit,
  owns payment-history;

credit-card sub entity,
  owns interest-rate,
  owns minimum-payment,
  owns late-fee;

bank sub entity,
  owns bank-name;

credit-card-pros sub entity,
  owns pro;

ownership sub relation,
  relates owned-card,
  relates card-owner;

credit-card-user plays ownership:card-owner;
credit-card plays ownership:owned-card;

issuance sub relation,
  relates issued-card,
  relates card-issuer;

bank plays issuance:card-issuer;
credit-card plays issuance:issued-card;

benefit sub relation,
  relates beneficial-card,
  relates associated-pro;

credit-card plays benefit:beneficial-card;
credit-card-pros plays benefit:associated-pro;
"""



