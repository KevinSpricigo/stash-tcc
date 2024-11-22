import flet as ft
from passlib.hash import pbkdf2_sha256
from banco.conexao2 import supabase

async def registro_profissional(page: ft.Page):
    page.title = 'STASH - Registro Profissional' 
    page.bgcolor = '#2ECC71'
    page.window.resizable = True

    page.fonts = {
        'Poppins Regular': 'fonts/Poppins-Regular.ttf',
        'Poppins Semi-Bold': 'fonts/Poppins-SemiBold.ttf',
        'Poppins Bold': 'fonts/Poppins-Bold.ttf'
    }

    logo = ft.Container(
        ft.Image(
            src='img/STASH.png',
            width=130,
            height=130
        ),
        alignment=ft.alignment.center,
        margin=ft.margin.only(top=0)
    )

    titulo = ft.Container(
        ft.Text(
            value='Registre para ser um profissional',
            font_family='Poppins Semi-Bold',
            color='#FFFFFF',
            size=18
        ),
        alignment=ft.alignment.center,
        margin=ft.margin.only(top=-50)
    )

    nome_layout = ft.Container(
        content=ft.Column([
            ft.Text(
                value='Nome',
                color='#FFFFFF',
                size=12,
                font_family='Poppins Regular'
            ),
            ft.TextField(
                border_color='#FFFFFF',
                color='#FFFFFF',
                cursor_color='#FFFFFF',
                width=335,
                height=56
            )
        ]),
        alignment=ft.alignment.center,
        margin=ft.margin.only(top=0),
        padding=10
    )

    sobrenome_layout = ft.Container(
        content=ft.Column([
            ft.Text(
                value='Sobrenome',
                color='#FFFFFF',
                size=12,
                font_family='Poppins Regular'
            ),
            ft.TextField(
                border_color='#FFFFFF',
                color='#FFFFFF',
                cursor_color='#FFFFFF',
                width=335,
                height=56
            )
        ]),
        alignment=ft.alignment.center,
        margin=ft.margin.only(top=-25),
        padding=10
    )

    telefone_layout = ft.Container(
        content=ft.Column([
            ft.Text(
                value='Telefone',
                color='#FFFFFF',
                size=12,
                font_family='Poppins Regular'
            ),
            ft.TextField(
                border_color='#FFFFFF',
                color='#FFFFFF',
                cursor_color='#FFFFFF',
                width=335,
                height=56
            )
        ]),
        alignment=ft.alignment.center,
        margin=ft.margin.only(top=-25),
        padding=10
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
                can_reveal_password=True 
            )
        ]),
        padding=10,
        alignment=ft.alignment.center,
        margin=ft.margin.only(top=-25)
    )

    async def mostrar_mensagem(mensagem: str):
        snack_bar = ft.SnackBar(content=ft.Text(mensagem))
        page.overlay.append(snack_bar)
        snack_bar.open = True
        page.update()

    def voltar_login(e):
        page.go("/login")

    tenhoConta_btn = ft.Container(
        ft.TextButton(
            text="Já tenho uma conta",
            style=ft.ButtonStyle(
                color={"": ft.colors.WHITE},
                bgcolor={"": ft.colors.TRANSPARENT},
            ),
            on_click=voltar_login
        ),
        alignment=ft.alignment.center,
        margin=ft.margin.only(top=-10)
    )

    def voltar_registro(e):
        page.go('/registro')

    voltar = ft.IconButton(
        icon=ft.icons.ARROW_BACK_IOS,
        icon_color='white',
        on_click=voltar_registro
    )

    async def registrar_profissional(e):
        nome = nome_layout.content.controls[1].value
        sobrenome = sobrenome_layout.content.controls[1].value
        telefone = telefone_layout.content.controls[1].value
        senha = senha_layout.content.controls[1].value

        if not all([nome, sobrenome, telefone, senha]):
            await mostrar_mensagem("Por favor, preencha todos os campos.")
            return

        try:
            resultado = supabase.table('profissionais')\
                .select('telefone')\
                .eq('telefone', telefone)\
                .execute()

            if resultado.data:
                await mostrar_mensagem("Este telefone já está cadastrado.")
                return

            senha_hash = pbkdf2_sha256.hash(senha)
            dados_profissional = {
                "nome": nome,
                "sobrenome": sobrenome,
                "telefone": telefone,
                "senha": senha_hash,
                "status": "Indisponível",
                "profissao": "Não especificada"
            }

            resultado = supabase.table('profissionais')\
                .insert(dados_profissional)\
                .execute()

            if resultado.data:
                await mostrar_mensagem("Registro realizado com sucesso!")
                page.go("/login")
            else:
                await mostrar_mensagem("Erro ao registrar. Tente novamente.")

        except Exception as e:
            await mostrar_mensagem(f"Erro ao registrar: {str(e)}")

    registrar_btn = ft.Container(
        ft.ElevatedButton(
            content=ft.Text(
                value='Registrar',
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
            on_click=registrar_profissional
        ),
        padding=10,
        alignment=ft.alignment.center,
        margin=ft.margin.only(top=-12)
    )

    page.add(
        logo,
        titulo,
        nome_layout,
        sobrenome_layout,
        telefone_layout,
        senha_layout,
        registrar_btn,
        tenhoConta_btn,
        voltar
    )