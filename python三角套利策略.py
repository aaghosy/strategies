class fmz_market():
    def basic_market_data(self, idx):
        # idx: 0/1/2 对应 exchanges[0..2]
        depth = exchanges[idx].GetDepth()
        if not depth or not depth.Bids or not depth.Asks:
            Log("深度数据为空或格式异常")
            return None
        
        # 检查买一和卖一是否存在
        if len(depth.Bids) == 0 or len(depth.Asks) == 0:
            Log("买一或卖一数据为空")
            return None

        bid1 = depth.Bids[0]   # 买一
        ask1 = depth.Asks[0]   # 卖一

        Log("买一价:", bid1.Price, "买一量:", bid1.Amount,
            "卖一价:", ask1.Price, "卖一量:", ask1.Amount)

        return {
            "bid_price": bid1.Price,
            "bid_volume": bid1.Amount,
            "ask_price": ask1.Price,
            "ask_volume": ask1.Amount
        }
    def profit_calculation(self, amount, tax_rate):
        """
        三角套利利润计算
        amount: 初始交易量
        tax_rate: 手续费率（如 0.001 表示 0.1%）
        
        假设三个交易对：
        P1: A/B, P2: B/C, P3: A/C
        """
        
        profit_obtain = 0  # ✅ 初始化返回值
        
        # 获取三个交易对的深度数据
        p1_depth = self.basic_market_data(0)
        p2_depth = self.basic_market_data(1)
        p3_depth = self.basic_market_data(2)
        
        # 检查数据是否有效
        if not p1_depth or not p2_depth or not p3_depth:
            Log("获取深度数据失败")
            return 0
        
        # 提取价格和成交量
        p1_sale_price = p1_depth['bid_price']
        p2_sale_price = p2_depth['bid_price']
        p3_sale_price = p3_depth['bid_price']
        p1_buy_price = p1_depth['ask_price']
        p2_buy_price = p2_depth['ask_price']
        p3_buy_price = p3_depth['ask_price']
        p1_sale_volume = p1_depth['bid_volume']
        p2_sale_volume = p2_depth['bid_volume']
        p3_sale_volume = p3_depth['bid_volume']
        p1_buy_volume = p1_depth['ask_volume']
        p2_buy_volume = p2_depth['ask_volume']
        p3_buy_volume = p3_depth['ask_volume']
        
        # 情况1: p1_sale_price / p2_sale_price < p3_sale_price
        if p1_sale_price / p2_sale_price < p3_sale_price:
            # ✅ 修复：Q3 → amount, tax → tax_rate
            tax_amount = (p1_buy_price + p2_sale_price * p3_sale_price + p2_sale_price * p3_buy_price) * amount * tax_rate 
            profit_obtain = (p3_sale_price - p1_buy_price / p2_sale_price) * amount * p2_buy_price
            Log('P1:', p1_buy_price, 'P2:', p2_sale_price, 'P3:', p3_sale_price, 'Tax:', tax_amount, 'Profit:', profit_obtain)
            
            # 如果手续费大于利润，无利可图
            if tax_amount > profit_obtain:
                return 0
        
        # 情况2: p1_sale_price / p2_sale_price > p3_sale_price
        elif p1_sale_price / p2_sale_price > p3_sale_price:
            # ✅ 修复：Q3 → amount, tax → tax_rate
            tax_amount = (p1_buy_price + p2_sale_price * p3_sale_price + p2_sale_price * p3_buy_price) * amount * tax_rate 
            profit_obtain = (p1_buy_price / p2_sale_price - p3_sale_price) * amount * p2_buy_price
            Log('P1:', p1_buy_price, 'P2:', p2_sale_price, 'P3:', p3_sale_price, 'Tax:', tax_amount, 'Profit:', profit_obtain)
            
            # 如果手续费大于利润，无利可图
            if tax_amount > profit_obtain:
                return 0
        
        return profit_obtain
    
    def profit_calculation_circle(self):
        usdt_amount = 0
        for i in range(10000):
            profit_obtain = self.profit_calculation()
            
