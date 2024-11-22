import flet as ft
from banco.conexao2 import supabase
from typing import Optional, Tuple

async def obter_info_profissional(id_profissional: int) -> Optional[Tuple[str, str, str]]:
    try:
        resultado = supabase.table('profissionais')\
            .select('nome, sobrenome, profissao')\
            .eq('id_profissional', id_profissional)\
            .limit(1)\
            .execute()
        
        if resultado.data:
            dados = resultado.data[0]
            return (dados['nome'], dados['sobrenome'], dados['profissao'])
        return None
    except Exception as e:
        print(f"Erro ao obter informações do profissional: {e}")
        return None

async def atualizar_profissional(id_profissional: int, nome: str, profissao: str) -> bool:
    try:
        nome_partes = nome.split()
        primeiro_nome = nome_partes[0]
        sobrenome = " ".join(nome_partes[1:]) if len(nome_partes) > 1 else ""
        
        dados_atualizacao = {
            "nome": primeiro_nome,
            "sobrenome": sobrenome,
            "profissao": profissao
        }
        
        resultado = supabase.table('profissionais')\
            .update(dados_atualizacao)\
            .eq('id_profissional', id_profissional)\
            .execute()
        
        return len(resultado.data) > 0
    except Exception as e:
        print(f"Erro ao atualizar profissional: {e}")
        return False

async def configuracao(page: ft.Page):
    if not hasattr(page, 'session_data'):
        page.session_data = {}
        page.go('/login')
        return
    page.fonts = {
        'Poppins Regular': 'Poppins-Regular.ttf'
    }

    id_profissional = page.session_data.get("user_id")
    info_profissional = await obter_info_profissional(id_profissional)

    if not info_profissional:
        page.go('/login')
        return

    async def mostrar_mensagem(mensagem: str):
        snack = ft.SnackBar(content=ft.Text(mensagem))
        page.overlay.append(snack)
        snack.open = True
        page.update()

    def pick_files_result(e: ft.FilePickerResultEvent):
        if e.files:
            imagem_selecionada = e.files[0]
            avatar_imagem.src = imagem_selecionada.path
            avatar_imagem.visible = True
            avatar_icon.visible = False
            page.update()

    def on_avatar_click(e):
        pick_files_dialog.pick_files(
            allow_multiple=False,
            allowed_extensions=['png', 'jpg', 'jpeg']
        )

    async def salvar_alteracoes(e):
        nome = nome_campo.value
        profissao = profissao_campo.value

        if not nome or not profissao:
            await mostrar_mensagem("Por favor, preencha todos os campos.")
            return

        if await atualizar_profissional(id_profissional, nome, profissao):
            await mostrar_mensagem("Informações atualizadas com sucesso!")
        else:
            await mostrar_mensagem("Erro ao atualizar informações.")

    pick_files_dialog = ft.FilePicker(on_result=pick_files_result)
    page.overlay.append(pick_files_dialog)

    avatar_icon = ft.Icon(ft.icons.PERSON, size=40, color=ft.colors.BLUE)
    avatar_imagem = ft.Image(
        visible=False,
        width=80,
        height=80,
        fit=ft.ImageFit.COVER,
        border_radius=40
    )

    avatar_container = ft.Container(
        content=ft.Stack([
            ft.Container(
                content=avatar_icon,
                width=80,
                height=80,
                border_radius=40,
                bgcolor=ft.colors.BLUE_50,
            ),
            avatar_imagem,
        ]),
        on_click=on_avatar_click,
        ink=True,
        tooltip="Clique para selecionar uma imagem"
    )

    nome_campo = ft.TextField(
        border_color='#2ECC71',
        color='black',
        cursor_color='#2ECC71',
        width=400,
        text_style=ft.TextStyle(size=14),
        hint_text="Nome",
        hint_style=ft.TextStyle(color='#BDBDBD'),
        read_only=True,
        value=f"{info_profissional[0]} {info_profissional[1]}"
    )

    profissao_campo = ft.TextField(
        border_color='#2ECC71',
        color='black',
        cursor_color='#2ECC71',
        width=400,
        text_style=ft.TextStyle(size=14),
        hint_text="Eletrecista, Pintor, Limpador",
        hint_style=ft.TextStyle(color='#BDBDBD'),
        value=info_profissional[2]
    )

    def fazer_logout(e):
        page.session_data.clear()
        page.go('/login')

    info = ft.Container(
        content=ft.Column([
            avatar_container,
            nome_campo,
            profissao_campo,
            ft.ElevatedButton(
                content=ft.Text(
                    value='Salvar',
                    size=14,
                    color='#FFFFFF',
                    font_family='Poppins Regular'
                ),
                style=ft.ButtonStyle(
                    shape=ft.RoundedRectangleBorder(radius=32),
                    bgcolor='#2ECC71'
                ),
                width=200,
                height=40,
                on_click=salvar_alteracoes
            )
        ],
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER
        ),
        alignment=ft.alignment.center,
        padding=ft.padding.only(top=200, left=8, right=8)
    )

    sair = ft.Container(
        ft.IconButton(
            icon=ft.icons.LOGOUT,
            icon_color='red',
            tooltip="Sair",
            on_click=fazer_logout
        ),
        alignment=ft.alignment.top_right
    )

    page.add(
        info,
        sair
    )