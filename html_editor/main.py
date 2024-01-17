import bs4


def create_html(path: str, account: str):
    """

    :param path: destination path to creating html file
    :param account: account name
    :return:
    """
    html = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Wat account is</title>
</head>
<body>

</body>
</html>"""
    soup = bs4.BeautifulSoup(html, 'html.parser')
    title = soup.find("title")
    title.string = account
    with open(path, "wb") as out:
        out.write(soup.prettify("utf-8"))


if __name__ == '__main__':
    create_html("./init_new.html", "v2 - 91")
