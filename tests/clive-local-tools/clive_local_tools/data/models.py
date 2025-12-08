from __future__ import annotations

from dataclasses import dataclass, field

import test_tools as tt


@dataclass
class AccountData:
    account: tt.Account
    hives_liquid: tt.Asset.TestT
    hbds_liquid: tt.Asset.TbdT
    vests: tt.Asset.TestT  # in hive power
    hives_savings: tt.Asset.TestT = field(default_factory=lambda: tt.Asset.Test(0))
    hbds_savings: tt.Asset.TbdT = field(default_factory=lambda: tt.Asset.Tbd(0))
    hives_savings_withdrawal: tt.Asset.TestT = field(default_factory=lambda: tt.Asset.Test(0))
    hbds_savings_withdrawal: tt.Asset.TbdT = field(default_factory=lambda: tt.Asset.Tbd(0))

    @property
    def from_savings_transfer_count(self) -> int:
        return sum([self.hives_savings_withdrawal > 0, self.hbds_savings_withdrawal > 0])
