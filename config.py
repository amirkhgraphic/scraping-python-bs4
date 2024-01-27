BASE_URL = ('https://www.homegate.ch/{type}/real-estate/city-{city}/matching-list?'
            'ac={min_rooms}&ad={max_rooms}&{min_price_param}={min_price}&'
            '{max_price_param}={max_price}&ipd=true')

price_params = {
    'rent': ('ag', 'ah'),
    'buy': ('ai', 'aj')
}
