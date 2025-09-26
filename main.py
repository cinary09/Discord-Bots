meme_dict = {
            "CRINGE": "Garip ya da utandırıcı bir şey",
            "LOL": "Komik bir şeye verilen cevap",
            "GG": "iyi oyundu başarılar",
            "EZ": "kolaydı",
            "IRL": "gerçek dünyada",
            "SMT": "birşey",
            "IDC": "başının çaresine bak"
            }

word = input("Anlamadığınız bir kelime yazın (hepsini büyük harflerle yazın!): ")

if word in meme_dict.keys():
        print(meme_dict[word])
else:
    print("Syntax Error")
