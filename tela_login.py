import flet as ft
from banco.conexao2 import supabase
from passlib.hash import pbkdf2_sha256
from banco.sessao import registrar_acesso, criar_token_sessao, obter_tipo_usuario, obter_ipv6
import asyncio

async def login(page: ft.Page):
    if not hasattr(page, 'session_data'):
        page.session_data = {}
        
    page.title = "STASH - Login"
    page.bgcolor = "#2ECC71"
    page.padding = 0
    page.controls.clear()

    page.fonts = {
        "Poppins Semi-Bold": "fonts/Poppins-SemiBold.ttf",
        "Poppins Regular": "fonts/Poppins-Regular.ttf",
        "Poppins Bold": "fonts/Poppins-Bold.ttf",
    }

    def show_snack_bar(message: str):
        snack = ft.SnackBar(content=ft.Text(message))
        page.snack_bar = snack
        snack.open = True
        page.update()

    async def autenticar_usuario(e):
        try:
            telefone = telefone_layout.content.controls[1].value
            senha = senha_layout.content.controls[1].value

            if not telefone or not senha:
                show_snack_bar("Por favor, preencha todos os campos")
                return

            resultado = supabase.table('pessoas')\
                .select('id_pessoa, senha')\
                .eq('telefone', telefone)\
                .limit(1)\
                .execute()
            
            tipo_usuario = "usuario"
            usuario = resultado.data[0] if resultado.data else None

            if not usuario:
                resultado = supabase.table('profissionais')\
                    .select('id_profissional, senha')\
                    .eq('telefone', telefone)\
                    .limit(1)\
                    .execute()
                tipo_usuario = "profissional"
                usuario = resultado.data[0] if resultado.data else None

            if not usuario:
                show_snack_bar("Usuário não encontrado ou senha incorreta")
                return

            id_usuario = usuario['id_pessoa'] if tipo_usuario == "usuario" else usuario['id_profissional']
            senha_hash = usuario['senha']

            if not pbkdf2_sha256.verify(senha, senha_hash):
                show_snack_bar("Usuário não encontrado ou senha incorreta")
                return

            ip_usuario = await obter_ipv6()
            id_log = await registrar_acesso(id_usuario, tipo_usuario, ip_usuario)

            if not id_log:
                show_snack_bar("Erro ao registrar acesso")
                return

            try:
                token = criar_token_sessao()
                page.session_data["user_id"] = id_usuario
                page.session_data["user_type"] = tipo_usuario
                page.session_data["session_token"] = token

                show_snack_bar(f"Login de {tipo_usuario} realizado com sucesso!")
                await asyncio.sleep(1)
                
                page.update()
                
                if tipo_usuario == "profissional":
                    page.go('/home-profissional')
                else:
                    page.go('/home-usuario')
                    
            except Exception as e:
                print(f"Erro ao salvar sessão: {e}")
                show_snack_bar("Erro ao salvar dados da sessão")

        except Exception as e:
            print(f"Erro no login: {e}")
            show_snack_bar(f"Erro ao fazer login: {str(e)}")

    logo = ft.Container(
        ft.Image(
            src='img/STASH.png',
            width=273,
            height=293
        ),
        alignment=ft.alignment.center,
        margin=ft.margin.only(top=-60)
    )

    titulo = ft.Container(
        ft.Text(
            value='Comece a usar o app da Stash',
            size=18,
            color='white',
            font_family='Poppins Semi-Bold'
        ),
        alignment=ft.alignment.center,
        margin=ft.margin.only(top=-160)
    )

    telefone_layout = ft.Container(
        content=ft.Column([
            ft.Text(
                value='Telefone',
                size=12,
                font_family='Poppins Regular',
                color='white'
            ),
            ft.TextField(
                border_color='white',
                color='white',
                cursor_color='white',
                width=335,
                height=56,
            )
        ]),
        padding=10,
        alignment=ft.alignment.center,
        margin=ft.margin.only(top=-35)
    )

    senha_layout = ft.Container(
        content=ft.Column([
            ft.Text(
                value='Senha',
                size=12,
                font_family='Poppins Regular',
                color='white'
            ),
            ft.TextField(
                border_color='white',
                color='white',
                cursor_color='white',
                width=335,
                height=56,
                password=True,
                can_reveal_password=True,
            )
        ]),
        padding=10,
        alignment=ft.alignment.center,
        margin=ft.margin.only(top=-15)
    )

    entrar_btn = ft.Container(
        ft.ElevatedButton(
            content=ft.Text(
                value='Entrar',
                size=18,
                color='#2ECC71',
                font_family='Poppins Bold'
            ),
            style=ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(radius=32),
                bgcolor='white'
            ),
            width=335,
            height=50,
            on_click=autenticar_usuario
        ),
        padding=10,
        alignment=ft.alignment.center,
        margin=ft.margin.only(top=-10)
    )

    def ir_registro(e):
        page.go("/registro")

    registar = ft.Container(
        ft.TextButton(
            text="Não tenho uma conta",
            style=ft.ButtonStyle(
                color={"": ft.colors.WHITE},
                bgcolor={"": ft.colors.TRANSPARENT},
            ),
            on_click=ir_registro
        ),
        alignment=ft.alignment.center
    )

    page.add(
        logo,
        titulo,
        telefone_layout,
        senha_layout,
        entrar_btn,
        registar
    )