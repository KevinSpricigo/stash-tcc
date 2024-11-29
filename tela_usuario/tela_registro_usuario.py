import flet as ft
from banco.conexao2 import supabase
from passlib.hash import pbkdf2_sha256

async def registro(page: ft.Page):
    page.title = 'STASH - Registro Usuário'
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
            value='Seja um usuário',
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

    async def verificar_telefone_existente(telefone: str) -> bool:
        try:
            resultado = supabase.table('pessoas')\
                .select('id_pessoa')\
                .eq('telefone', telefone)\
                .execute()
            
            return len(resultado.data) > 0
        except Exception as e:
            print(f"Erro ao verificar telefone: {e}")
            return False

    async def registrar_usuario(e):
        try:
            nome = nome_layout.content.controls[1].value
            sobrenome = sobrenome_layout.content.controls[1].value
            telefone = telefone_layout.content.controls[1].value
            senha = senha_layout.content.controls[1].value

            if not all([nome, sobrenome, telefone, senha]):
                page.show_snack_bar(
                    ft.SnackBar(content=ft.Text("Por favor, preencha todos os campos."))
                )
                return

            if await verificar_telefone_existente(telefone):
                page.show_snack_bar(
                    ft.SnackBar(content=ft.Text("Este telefone já está cadastrado."))
                )
                return

            senha_hash = pbkdf2_sha256.hash(senha)

            resultado_endereco = supabase.table('endereco').insert({
                'cidade': 'Criciúma',  
                'bairro': 'Não Especificado', 
                'rua': 'Não Especificado',     
                'numero': 0 
            }).execute()
            
            if not resultado_endereco.data:
                raise Exception("Falha ao criar endereço")

            id_endereco = resultado_endereco.data[0]['id_endereco']

            dados_usuario = {
                "nome": nome,
                "sobrenome": sobrenome,
                "telefone": telefone,
                "senha": senha_hash,
                "id_endereco": id_endereco
            }

            resultado = supabase.table('pessoas')\
                .insert(dados_usuario)\
                .execute()

            if resultado.data:
                page.show_snack_bar(
                    ft.SnackBar(content=ft.Text("Registro realizado com sucesso!"))
                )
                page.go("/login")
            else:
                raise Exception("Falha ao inserir usuário")

        except Exception as e:
            page.show_snack_bar(
                ft.SnackBar(content=ft.Text(f"Erro ao registrar: {str(e)}"))
            )

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
            on_click=registrar_usuario
        ),
        padding=10,
        alignment=ft.alignment.center,
        margin=ft.margin.only(top=-12)
    )

    def ir_registro_profissional(e):
        page.go("/registro-profissional")

    registar_profisional = ft.Container(
        ft.TextButton(
            text="Trabalhe com o app",
            style=ft.ButtonStyle(
                color={"": ft.colors.WHITE},
                bgcolor={"": ft.colors.TRANSPARENT},
            ),
            on_click=ir_registro_profissional
        ),
        alignment=ft.alignment.center,
        margin=ft.margin.only(top=-10)
    )

    def voltar_login(e):
        page.go('/login')

    voltar = ft.IconButton(
        icon=ft.icons.ARROW_BACK_IOS,
        icon_color='white',
        on_click=voltar_login
    )

    page.add(
        logo,
        titulo,
        nome_layout,
        sobrenome_layout,
        telefone_layout,
        senha_layout,
        registrar_btn,
        registar_profisional,
        voltar
    )