from tgtg import TgtgClient

client = TgtgClient(access_token="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE3MDk5OTMxMzUsImlhdCI6MTcwOTgyMDMzNSwiaXNzIjoidGd0Z19zb3RlcmlhIiwidCI6InRzU2IyeVFZUmZlc2Q1dzNRbUFNQXc6MDoxIiwic3ViIjoiMTE2Nzc1NjIzIn0.SInxMXQIy49GmCz8Z_C-6uOF69mmh8ce_HtxLUyqJto",
                    refresh_token="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE3NDEzNTYzMzUsImlhdCI6MTcwOTgyMDMzNSwiaXNzIjoidGd0Z19zb3RlcmlhIiwidCI6IkhoeXdsQ2dzU1ZDWExSMTlCNEZqTlE6MDowIiwic3ViIjoiMTE2Nzc1NjIzIn0.1Wn08UywX61BOIDQlmZmz8rV6d19LXUi7Uo4JHEnt8Q", 
                    user_id="116775623", cookie="datadome=qFIMqCFOombG9jywFCc7g1h3IXzR_FGwvC2f87ZdFPApyb~xRX1YH6IJ17NPOHmXACrY5inC5_PXoBHKwje89xM3_yy85XNjuzteOIgcolkHfg3Pq1B1CNF52wJigchx; Max-Age=5184000; Domain=.apptoogoodtogo.com; Path=/; Secure; SameSite=Lax")

items = client.get_items(
        favorites_only=True,
        latitude=51.941248,
        longitude=15.504714,
        radius=10,
    )

print(items)