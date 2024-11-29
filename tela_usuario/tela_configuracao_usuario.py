import flet as ft
from banco.conexao2 import supabase
from typing import Optional, Tuple
import os
import time

async def upload_avatar(file_path: str, id_usuario: str) -> bool:
    try:
        if not os.path.exists(file_path):
            print(f"Arquivo não encontrado: {file_path}")
            return False

        old_avatar = supabase.table('pessoas')\
            .select('avatar_url')\
            .eq('id_pessoa', id_usuario)\
            .execute()

        if old_avatar.data:
            old_avatar_url = old_avatar.data[0].get('avatar_url')
            if old_avatar_url:
                old_avatar_path = old_avatar_url.split('/avatars/')[-1].split('?')[0]
                delete_result = supabase.storage.from_('avatars').remove([old_avatar_path])
                if not delete_result:
                    print(f"Falha ao deletar avatar anterior: {old_avatar_path}")

        with open(file_path, "rb") as file:
            file_bytes = file.read()
            timestamp = int(time.time())
            file_name = f"avatar_user_{id_usuario}.jpg"
            
            result = supabase.storage.from_('avatars').upload(file_name, file_bytes)

            if result:
                public_url = f"{supabase.url}/storage/v1/object/public/avatars/{file_name}?v={timestamp}"
                
                update_result = supabase.table('pessoas')\
                    .update({'avatar_url': public_url})\
                    .eq('id_pessoa', id_usuario)\
                    .execute()
                
                if update_result.data:
                    return True

        print("Falha ao fazer upload do avatar.")
        return False

    except Exception as e:
        print(f"Erro ao fazer upload do avatar: {e}")
        return False

async def obter_info_usuario(id_usuario: int) -> Optional[Tuple[str, str, str, str, str, str, str]]:
    try:
        timestamp = int(time.time())
        
        resultado = supabase.table('pessoas')\
            .select('nome, sobrenome, id_endereco, avatar_url')\
            .eq('id_pessoa', id_usuario)\
            .execute()
        
        if not resultado.data or len(resultado.data) == 0:
            print("Usuário não encontrado")
            return None

        dados = resultado.data[0]
        id_endereco = dados.get('id_endereco')
        avatar_url = dados.get('avatar_url')

        if avatar_url:
            base_url = avatar_url.split('?')[0]
            avatar_url = f"{base_url}?v={timestamp}"

        if not id_endereco:
            return (
                dados['nome'],
                dados['sobrenome'],
                "Não especificado",
                "Não especificado",
                "Não especificado",
                "0",
                avatar_url
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
                "0",
                avatar_url
            )

        endereco = endereco_resultado.data[0]
        return (
            dados['nome'],
            dados['sobrenome'],
            endereco['cidade'],
            endereco['bairro'],
            endereco['rua'],
            str(endereco['numero']),
            avatar_url
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
    selected_file_path = None
    
    if not info_usuario:
        page.go('/login')
        return

    async def mostrar_mensagem(mensagem: str):
        snack = ft.SnackBar(content=ft.Text(mensagem))
        page.overlay.append(snack)
        snack.open = True
        page.update()

    def pick_files_result(e: ft.FilePickerResultEvent):
        nonlocal selected_file_path
        if e.files and len(e.files) > 0:
            selected_file_path = e.files[0].path
            avatar_imagem.src = selected_file_path
            avatar_imagem.visible = True
            avatar_icon.visible = False
            page.update()

    def fazer_logout(e):
        page.session_data.clear()
        page.go('/login')

    async def atualizar_avatar_ui(nova_url: str):
        avatar_imagem.src = nova_url
        avatar_imagem.visible = True
        avatar_icon.visible = False
        page.update()

    async def salvar_alteracoes(e):
        progresso.visible = True
        page.update()
        
        nome = nome_campo.value
        sobrenome = sobrenome_campo.value
        cidade = cidade_campo.value
        bairro = bairro_campo.value
        rua = rua_campo.value
        numero = numero_campo.value
        
        if not nome or not sobrenome or not cidade or not bairro or not rua or not numero:
            progresso.visible = False
            page.update()
            await mostrar_mensagem("Por favor, preencha todos os campos.")
            return

        success = await atualizar_usuario(id_usuario, nome, sobrenome, cidade, bairro, rua, numero)

        if selected_file_path:
            avatar_success = await upload_avatar(selected_file_path, id_usuario)
            if avatar_success:
                timestamp = int(time.time())
                new_url = f"{supabase.url}/storage/v1/object/public/avatars/avatar_user_{id_usuario}.jpg?v={timestamp}"
                await atualizar_avatar_ui(new_url)
            else:
                await mostrar_mensagem("Erro ao atualizar avatar, mas dados foram salvos.")

        progresso.visible = False
        page.update()

        if success:
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

    avatar_icon = ft.Icon(
        ft.icons.PERSON, 
        size=40, 
        color=ft.colors.BLUE,
        visible=not info_usuario[6]
    )
   
    avatar_imagem = ft.Image(
        src=info_usuario[6] if info_usuario[6] else None,
        visible=bool(info_usuario[6]),
        width=80,
        height=80,
        fit=ft.ImageFit.COVER,
        border_radius=40
    )

    progresso = ft.ProgressRing(
        width=16,
        height=16,
        stroke_width=2,
        color="#2ECC71",
        visible=False
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
        focused_border_color='#2ECC71',
        color='black',
        label="Nome",
        value=info_usuario[0],
        cursor_color='#2ECC71',
        width=400,
        label_style=ft.TextStyle(color='black')
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
        focused_border_color='#2ECC71',
        color='black',
        label="Sobrenome",
        value=info_usuario[1],
        cursor_color='#2ECC71',
        width=400,
        label_style=ft.TextStyle(color='black')
    )
    cidade_campo = ft.TextField(
        focused_border_color='#2ECC71',
        color='black',
        label="Cidade",
        value=info_usuario[2],
        cursor_color='#2ECC71',
        width=400,
        label_style=ft.TextStyle(color='black')
    )
    bairro_campo = ft.TextField(
        focused_border_color='#2ECC71',
        color='black',
        label="Bairro",
        value=info_usuario[3],
        cursor_color='#2ECC71',
        width=400,
        label_style=ft.TextStyle(color='black')
    )
    rua_campo = ft.TextField(
        focused_border_color='#2ECC71',
        color='black',
        label="Rua",
        value=info_usuario[4],
        cursor_color='#2ECC71',
        width=400,
        label_style=ft.TextStyle(color='black')
    )
    numero_campo = ft.TextField(
        focused_border_color='#2ECC71',
        color='black',
        label="Numero",
        value=info_usuario[5],
        cursor_color='#2ECC71',
        width=400,
        label_style=ft.TextStyle(color='black')
    )

    botao_salvar = ft.Row(
        [
            ft.ElevatedButton(
                content=ft.Row(
                    [
                        ft.Text(
                            value='Salvar',
                            size=14,
                            color='#FFFFFF',
                            font_family='Poppins Regular'
                        ),
                        progresso,
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
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
            botao_salvar
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