import flet as ft
from banco.conexao2 import supabase
from typing import Optional, Tuple

async def obter_info_usuario(id_usuario: int) -> Optional[Tuple[str, str, str, str, str, str]]:
    try:
        resultado = supabase.table('pessoas')\
            .select('nome, sobrenome, id_endereco')\
            .eq('id_pessoa', id_usuario)\
            .execute()
        
        if not resultado.data or len(resultado.data) == 0:
            print("Usuário não encontrado")
            return None

        dados = resultado.data[0]
        id_endereco = dados.get('id_endereco')

        if not id_endereco:
            return (
                dados['nome'],
                dados['sobrenome'],
                "Não especificado",
                "Não especificado",
                "Não especificado",
                "0"
            )

        endereco_resultado = supabase.table('endereco')\
            .select('cidade, bairro, rua, numero')\
            .eq('id_endereco', id_endereco)\
            .execute()

        if not endereco_resultado.data or len(endereco_resultado.data) == 0:
            return (
                dados['nome'],
                dados['sobrenome'],
                "Não especificado",
                "Não especificado",
                "Não especificado",
                "0"
            )

        endereco = endereco_resultado.data[0]
        return (
            dados['nome'],
            dados['sobrenome'],
            endereco['cidade'],
            endereco['bairro'],
            endereco['rua'],
            str(endereco['numero'])
        )

    except Exception as e:
        print(f"Erro ao obter informações do usuário: {e}")
        return None

async def atualizar_usuario(id_usuario: int, nome: str, sobrenome: str, cidade: str, bairro: str, rua: str, numero: str) -> bool:
    try:
        dados_usuario = {
            "nome": nome,
            "sobrenome": sobrenome,
        }

        dados_usuario_endereco = {
            "cidade": cidade,
            "bairro": bairro,
            "rua": rua,
            "numero": numero
        }

        resultado_endereco = supabase.table('pessoas').select('id_endereco').eq('id_pessoa', id_usuario).execute()
        
        if not resultado_endereco.data:
            print("Endereço não encontrado para o usuário especificado.")
            return False
        
        id_endereco = resultado_endereco.data[0]['id_endereco']

        resultado_usuario = supabase.table('pessoas')\
            .update(dados_usuario)\
            .eq('id_pessoa', id_usuario)\
            .execute()
        
        resultado_usuario_endereco = supabase.table("endereco")\
            .update(dados_usuario_endereco)\
            .eq('id_endereco', id_endereco)\
            .execute()

        if (resultado_usuario.data) and (resultado_usuario_endereco.data):
            print(f"Sucesso")

        return True 
    
    except Exception as e:
        print(f"Erro ao atualizar dados do usuário: {e}")
        return False

async def congfiguracao_usuario(page: ft.Page):
    if not hasattr(page, 'session_data') or not page.session_data.get('user_id'):
        page.go('/login')
        return

    page.bgcolor = '#FFFFFF'
    
    id_usuario = page.session_data.get("user_id")
    info_usuario = await obter_info_usuario(id_usuario)
    
    if not info_usuario:
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

    def fazer_logout(e):
        page.session_data.clear()
        page.go('/login')

    async def salvar_alteracoes(e):
        nome = nome_campo.value
        sobrenome = sobrenome_campo.value
        cidade = cidade_campo.value
        bairro = bairro_campo.value
        rua = rua_campo.value
        numero = numero_campo.value
        
        if not nome or not sobrenome or not cidade or not bairro or not rua or not numero:
            await mostrar_mensagem("Por favor, preencha todos os campos.")
            return

        if await atualizar_usuario(id_usuario, nome, sobrenome, cidade, bairro, rua, numero):
            await mostrar_mensagem("Informações atualizadas com sucesso!")
        else:
            await mostrar_mensagem("Erro ao atualizar informações.")

    pick_files_dialog = ft.FilePicker(on_result=pick_files_result)
    page.overlay.append(pick_files_dialog)

    def on_avatar_click(e):
        pick_files_dialog.pick_files(
            allow_multiple=False,
            allowed_extensions=['png', 'jpg', 'jpeg']
        )

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
        label="Nome",
        value=info_usuario[0],
        color='black',
        cursor_color='#2ECC71',
        width=400,
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

    sobrenome_campo = ft.TextField(
        label="Sobrenome",
        value=info_usuario[1],
        color='black',
        cursor_color='#2ECC71',
        width=400,
    )
    cidade_campo = ft.TextField(
        label="Cidade",
        value=info_usuario[2],
        color='black',
        cursor_color='#2ECC71',
        width=400,
    )
    bairro_campo = ft.TextField(
        label="Bairro",
        value=info_usuario[3],
        color='black',
        cursor_color='#2ECC71',
        width=400,
    )
    rua_campo = ft.TextField(
        label="Rua",
        value=info_usuario[4],
        color='black',
        cursor_color='#2ECC71',
        width=400,
    )
    numero_campo = ft.TextField(
        label="Numero",
        value=info_usuario[5],
        color='black',
        cursor_color='#2ECC71',
        width=400,
    )

    info = ft.Container(
        content=ft.Column([
            avatar_container,
            nome_campo,
            sobrenome_campo,
            cidade_campo,
            bairro_campo,
            rua_campo,
            numero_campo,
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
        padding=ft.padding.only(top=20, left=8, right=8)
    )

    page.add(
        info,
        sair
    )