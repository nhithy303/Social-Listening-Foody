my_account = {
    'username': 'foodee_d46teeuq',
    'password': 'meiderato303161'
}

location = 'ho-chi-minh'

food_categories = [
    'sang-trong', 'buffet', 'nha-hang', 'an-vat-via-he', 'an-chay', 'cafe', 'quan-an', 'bar-pub',
    'quan-nhau', 'beer-club', 'tiem-banh', 'tiec-tan-noi', 'shop-online', 'giao-com-van-phong', 'Foodcourt'
]

def get_urls(url_type, **kwargs):
    if url_type == 'home':
        return f"https://www.foody.vn/{kwargs['route']}"
    if url_type == 'login':
        return f"https://id.foody.vn/account/login?returnUrl=https://www.foody.vn/{location}/{kwargs['category']}?CategoryGroup=food&c={kwargs['category']}"
    if url_type == 'page':
        return f"https://www.foody.vn/{location}/food/{kwargs['category']}?page={kwargs['page_num']}#!#page{kwargs['page_num']}"
    if url_type == 'restaurant':
        return [
            f"https://www.foody.vn{kwargs['res_name']}",
            f"https://shopeefood.vn{kwargs['res_name']}"
        ]
    return ''