import requests
from kivy.app import App


class MyFirebase():
    API_KEY = "AIzaSyAWsyuLBQHYzmEtsv1jW7CekhSzH1m9yIE"

    def criar_conta(self, email, senha):
        link = f"https://identitytoolkit.googleapis.com/v1/accounts:signUp?key={self.API_KEY}"
        # ==============================================================================================================
        # As informações passadas aqui, que estão na variável "info", tem que ser em ingles. Logo tem que ser "password"
        # e não "senha". vide documentação em: https://cloud.google.com/identity-platform/docs/use-rest-api?hl=pt-br
        # ==============================================================================================================
        info = {"email": email,
                "password": senha,
                "returnSecureToken": True}
        requisicao = requests.post(link, data=info)
        requisicao_dic = requisicao.json()

        meu_app = App.get_running_app()
        if requisicao.ok:
            # requisicao_dic["kind"]            ->  Não nos interessa neste momento
            # requisicao_dic["idToken"]         ->  IMPORTANTE: É a autenticação. É com esse parâmetro que dizemos a
            #                                       quê o usuário tem acesso. É o que garante que ele só deve ter acesso
            #                                       às suas informações. Exemplo.: que só ele pode alterar sua
            #                                       foto do perfil.
            # requisicao_dic["email"]           ->  Não nos interessa neste momento. Já temos.
            # requisicao_dic["expiresIn"]       ->  Não nos interessa neste momento. Mas significa "em quanto tempo" a
            #                                       senha expira.
            # requisicao_dic["refreshToken"]    ->  IMPORTANTE: Token que mantém o usuário logado. Com esse parâmetro,
            #                                       é possível o usuário LOGAR sem precisar informar novamente o seu.
            #                                       usuário e senha.
            # requisicao_dic["localId"]         ->  IMPORTANTE: ID do Usuário
            refresh_token = requisicao_dic["refreshToken"]
            local_id = requisicao_dic["localId"]
            id_token = requisicao_dic["idToken"]
            meu_app.local_id = local_id
            meu_app.id_token = id_token

            # Quando fechamos o app, todas as variáveis são descartadas. Como precisamos guardar o "refreshToken", uma
            # das formas é guardar em um arquivo.txt
            with open("refresh_token.txt", "w") as arquivo:
                arquivo.write(refresh_token)

            req_id_vendedor = requests.get(f"https://aplicativovendashash-edeaa-default-rtdb.firebaseio.com"
                                           f"/proximo_id_vendedor.json?auth={id_token}")
            id_vendedor = req_id_vendedor.json()

            link = f"https://aplicativovendashash-edeaa-default-rtdb.firebaseio.com/{local_id}.json?auth={id_token}"
            info_usuario = f'{{"avatar": "foto1.png", "equipe": "", "total_vendas": "0", "vendas": "", "id_vendedor": "{id_vendedor}"}}'
            requisicao_usuario = requests.patch(link, data=info_usuario)

            # Atualizar o valor do proximo_id_vendedor
            proximo_id_vendedor = int(id_vendedor) + 1
            info_id_vendedor = f'{{"proximo_id_vendedor": "{proximo_id_vendedor}"}}'
            requests.patch(f"https://aplicativovendashash-edeaa-default-rtdb.firebaseio.com/.json"
                           f"?auth={id_token}", data=info_id_vendedor)

            meu_app.carregar_infos_usuario()
            meu_app.mudar_tela("HomePage")
        else:
            mensagem_erro = requisicao_dic["error"]["message"]
            pagina_login = meu_app.root.ids["loginpage"]
            pagina_login.ids["mensagem_login"].text = mensagem_erro
            pagina_login.ids["mensagem_login"].color = (1, 0, 0, 1)

        print(requisicao_dic)

    def fazer_login(self, email, senha):
        link = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={self.API_KEY}"
        info = {"email": email,
                "password": senha,
                "returnSecureToken": True}
        requisicao = requests.post(link, data=info)
        requisicao_dic = requisicao.json()

        meu_app = App.get_running_app()
        if requisicao.ok:
            # requisicao_dic["kind"]            ->  Não nos interessa neste momento
            # requisicao_dic["idToken"]         ->  IMPORTANTE: É a autenticação. É com esse parâmetro que dizemos a
            #                                       quê o usuário tem acesso. É o que garante que ele só deve ter acesso
            #                                       às suas informações. Exemplo.: que só ele pode alterar sua
            #                                       foto do perfil.
            # requisicao_dic["email"]           ->  Não nos interessa neste momento. Já temos.
            # requisicao_dic["expiresIn"]       ->  Não nos interessa neste momento. Mas significa "em quanto tempo" a
            #                                       senha expira.
            # requisicao_dic["refreshToken"]    ->  IMPORTANTE: Token que mantém o usuário logado. Com esse parâmetro,
            #                                       é possível o usuário LOGAR sem precisar informar novamente o seu.
            #                                       usuário e senha.
            # requisicao_dic["localId"]         ->  IMPORTANTE: ID do Usuário
            refresh_token = requisicao_dic["refreshToken"]
            local_id = requisicao_dic["localId"]
            id_token = requisicao_dic["idToken"]
            meu_app.local_id = local_id
            meu_app.id_token = id_token

            # Quando fechamos o app, todas as variáveis são descartadas. Como precisamos guardar o "refreshToken", uma
            # das formas é guardar em um arquivo.txt
            with open("refresh_token.txt", "w") as arquivo:
                arquivo.write(refresh_token)

            meu_app.carregar_infos_usuario()
            meu_app.mudar_tela("HomePage")
        else:
            mensagem_erro = requisicao_dic["error"]["message"]
            pagina_login = meu_app.root.ids["loginpage"]
            pagina_login.ids["mensagem_login"].text = mensagem_erro
            pagina_login.ids["mensagem_login"].color = (1, 0, 0, 1)


    def trocar_token(self, refresh_token):
        link = f"https://securetoken.googleapis.com/v1/token?key={self.API_KEY}"
        info = {
            "grant_type": "refresh_token",
            "refresh_token": refresh_token
        }
        requisicao = requests.post(link, data=info)
        requisicao_dic = requisicao.json()
        local_id = requisicao_dic["user_id"]
        id_token = requisicao_dic["id_token"]
        return local_id, id_token