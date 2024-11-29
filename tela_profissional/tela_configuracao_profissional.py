import flet as ft
from banco.conexao2 import supabase
from typing import Optional, Tuple
import base64
import os
import time

async def upload_avatar(file_path: str, id_profissional: str) -> bool:
    try:
        if not os.path.exists(file_path):
            print(f"Arquivo não encontrado: {file_path}")
            return False

        old_avatar = supabase.table('profissionais')\
            .select('avatar_url')\
            .eq('id_profissional', id_profissional)\
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
            file_name = f"avatar_prof_{id_profissional}.jpg"
            
            result = supabase.storage.from_('avatars').upload(file_name, file_bytes)

            if result:
                public_url = f"{supabase.url}/storage/v1/object/public/avatars/{file_name}?v={timestamp}"
                
                update_result = supabase.table('profissionais')\
                    .update({'avatar_url': public_url})\
                    .eq('id_profissional', id_profissional)\
                    .execute()
                
                if update_result.data:
                    return True

        print("Falha ao fazer upload do avatar.")
        return False
    except Exception as e:
        print(f"Erro ao fazer upload do avatar: {e}")
        return False

async def obter_info_profissional(id_profissional: int) -> Optional[Tuple[str, str, str, str]]:
    try:
        timestamp = int(time.time())
        
        resultado = supabase.table('profissionais')\
            .select('nome, sobrenome, profissao, avatar_url')\
            .eq('id_profissional', id_profissional)\
            .limit(1)\
            .execute()
        
        if resultado.data:
            dados = resultado.data[0]
            avatar_url = dados.get('avatar_url')
            
            if avatar_url:
                base_url = avatar_url.split('?')[0]
                avatar_url = f"{base_url}?v={timestamp}"
                
            return (
                dados['nome'], 
                dados['sobrenome'], 
                dados['profissao'], 
                avatar_url
            )
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
    page.bgcolor = '#FFFFFF'

    id_profissional = page.session_data.get("user_id")
    info_profissional = await obter_info_profissional(id_profissional)
    selected_file_path = None

    if not info_profissional:
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

    def on_avatar_click(e):
        pick_files_dialog.pick_files(
            allow_multiple=False,
            allowed_extensions=['png', 'jpg', 'jpeg']
        )

    async def atualizar_avatar_ui(nova_url: str):
        avatar_imagem.src = nova_url
        avatar_imagem.visible = True
        avatar_icon.visible = False
        page.update()

    async def salvar_alteracoes(e):
        progresso.visible = True
        page.update()

        nome = nome_campo.value
        profissao = profissao_campo.value

        if not nome or not profissao:
            progresso.visible = False
            page.update()
            await mostrar_mensagem("Por favor, preencha todos os campos.")
            return

        success = await atualizar_profissional(id_profissional, nome, profissao)

        if selected_file_path:
            avatar_success = await upload_avatar(selected_file_path, id_profissional)
            if avatar_success:
                timestamp = int(time.time())
                new_url = f"{supabase.url}/storage/v1/object/public/avatars/avatar_prof_{id_profissional}.jpg?v={timestamp}"
                await atualizar_avatar_ui(new_url)
            else:
                await mostrar_mensagem("Erro ao atualizar avatar, mas dados foram salvos.")

        progresso.visible = False
        page.update()

        if success:
            await mostrar_mensagem("Informações atualizadas com sucesso!")
        else:
            await mostrar_mensagem("Erro ao atualizar informações.")

    def fazer_logout(e):
        page.session_data.clear()
        page.go('/login')

    pick_files_dialog = ft.FilePicker(on_result=pick_files_result)
    page.overlay.append(pick_files_dialog)

    avatar_icon = ft.Icon(
        ft.icons.PERSON, 
        size=40, 
        color=ft.colors.BLUE,
        visible=not info_profissional[3]
    )

    avatar_imagem = ft.Image(
        src=info_profissional[3] if info_profissional[3] else None,
        visible=bool(info_profissional[3]),
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
        hint_text="Eletrecista, Pintor, Jardineiro",
        hint_style=ft.TextStyle(color='#BDBDBD'),
        value=info_profissional[2]
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
            profissao_campo,
            botao_salvar
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