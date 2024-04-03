from django.db import models


# 股票
import app01.models


class Stock(models.Model):
    code = models.CharField(max_length=6, primary_key=True)
    title = models.CharField(max_length=10)

    def __str__(self):
        return self.code + ':' + self.title


class HoldingStocks(models.Model):
    # 股票代码
    code = models.ForeignKey(Stock, on_delete=models.CASCADE)
    # 股票手数
    number = models.IntegerField()
    # 买入价
    buy_price = models.FloatField()
    # 现价
    now_price = models.FloatField(null=True)
    # 用户id
    account_id = models.ForeignKey(app01.models.User, on_delete=models.CASCADE)
    # time
    buy_time = models.CharField(max_length=20, null=True)

