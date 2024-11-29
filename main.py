import flet as ft
import asyncio
from banco.sessao import verificar_sessao_ativa, obter_tipo_usuario
from tela_splash import splash
from tela_apresentacao import apresentacao
from tela_login import login
from tela_profissional.tela_registro_profissional import registro_profissional
from tela_profissional.tela_home_profissional import home_profissional
from tela_profissional.tela_criarServico_profissional import criarServico
from tela_profissional.tela_servicosSolicitados import servicosSolicitados
from tela_profissional.tela_listarServico import listarServico
from tela_profissional.tela_registro_servicos import registrosServicos
from tela_profissional.tela_configuracao_profissional import configuracao
from tela_usuario.tela_registro_usuario import registro
from tela_usuario.tela_home_usuario import home_usuario
from tela_usuario.tela_configuracao_usuario import congfiguracao_usuario

from tela_usuario.tela_listar_eletricistas import listar_eletricistas
from tela_usuario.tela_listar_pintores import listar_pintores
from tela_usuario.tela_listar_jardineiros import listar_jardineiros

from tela_usuario.tela_contrato_usuario import contratar
from tela_usuario.tela_pagamento_usuario import pagamentos
from tela_usuario.tela_conclusao_servico import conclusao_servico
from tela_usuario.tela_avaliacao_servico import avaliar

async def main(page: ft.Page):
    if not hasattr(page, 'session_data'):
        page.session_data = {}
    
    page.window.always_on_top = True
    
    page.fonts = {
        'Poppins Semi-Bold': 'fonts/Poppins-SemiBold.ttf',
        'Poppins Bold' : 'fonts/Poppins-Bold.ttf',
        'Poppins Medium' : 'fonts/Poppins-Medium.ttf'
    }

    def appbar_profissional(title=None, show_back=False):
        if title:
            page.appbar = ft.AppBar(
                leading=ft.IconButton(
                    ft.icons.ARROW_BACK,
                    icon_color='#2ECC71',
                    on_click=lambda _: page.go("/home-profissional")
                ) if show_back else None,
                title=ft.Text(title, font_family='Poppins Semi-Bold', size=16),
                center_title=True,
                bgcolor=ft.colors.WHITE,
                color=ft.colors.BLACK,
            )

            linha = ft.Container(
                ft.Divider(height=1, color='#ADADAD'),
                padding=ft.padding.only(top=0)
            )
            page.controls.insert(0, linha)
        else:
            page.appbar = None
        page.update()

    def mudar_navbar(e):
        selecionado = e.control.selected_index
        if selecionado == 0:
            page.go('/home-profissional')
        elif selecionado == 1:
            page.go('/configuracao-profissional')

    def navbar_profissional(show=True):
        if show:
            selected_index = -1
            if page.route == '/home-profissional':
                selected_index = 0
            elif page.route == '/configuracao-profissional':
                selected_index = 1
            page.navigation_bar = ft.NavigationBar(
                selected_index=selected_index,
                on_change=mudar_navbar,
                destinations=[
                    ft.NavigationBarDestination(
                        icon=ft.icons.HOME,
                        icon_content=ft.Icon(ft.icons.HOME, color="white"),
                        selected_icon_content=ft.Icon(ft.icons.HOME, color="#2ECC71")
                    ),
                    ft.NavigationBarDestination(
                        icon=ft.icons.PERSON,
                        icon_content=ft.Icon(ft.icons.PERSON, color="white"),
                        selected_icon_content=ft.Icon(ft.icons.PERSON, color="#2ECC71")
                        
                    )
                ],
                bgcolor='#2ECC71',
                indicator_color='#FFFFFF',
                scale=1.2,
                border=ft.border_radius.only(top_left=20, top_right=20)
            )
        else:
            page.navigation_bar = None
        page.update()

    def appbar_usuario(title=None, show_back=False):
        if title:
            page.appbar = ft.AppBar(
                leading=ft.IconButton(
                    ft.icons.ARROW_BACK,
                    icon_color='#2ECC71',
                    on_click=lambda _: page.go("/home-usuario")
                ) if show_back else None,
                title=ft.Text(title, font_family='Poppins Semi-Bold', size=16),
                center_title=True,
                bgcolor=ft.colors.WHITE,
                color=ft.colors.BLACK,
            )

            linha = ft.Container(
                ft.Divider(height=1, color='#ADADAD'),
                padding=ft.padding.only(top=0)
            )
            page.controls.insert(0, linha)
        else:
            page.appbar = None
        page.update()

    def mudar_navbar_usuario(e):
        selecionado = e.control.selected_index
        if selecionado == 0:
            page.go('/home-usuario')
        elif selecionado == 1:
            page.go('/conclusao-servico')
        elif selecionado == 2:
            page.go('/configuracao-usuario')

    def navbar_usuario(show=True):
        if show:
            selected_index = -1
            if page.route == '/home-usuario':
                selected_index = 0
            elif page.route == '/conclusao-conclusao':
                selected_index = 1
            elif page.route == '/configuracao-usuario':
                selected_index = 2
            page.navigation_bar = ft.NavigationBar(
                selected_index=selected_index,
                on_change=mudar_navbar_usuario,
                destinations=[
                    ft.NavigationBarDestination(
                        icon=ft.icons.HOME,
                        icon_content=ft.Icon(ft.icons.HOME, color="white"),
                        selected_icon_content=ft.Icon(ft.icons.HOME, color="#2ECC71")
                    ),
                    ft.NavigationBarDestination(
                        icon=ft.icons.LIST,
                        icon_content=ft.Icon(ft.icons.LIST, color="white"),
                        selected_icon_content=ft.Icon(ft.icons.LIST, color="#2ECC71")
                        
                    ),
                    ft.NavigationBarDestination(
                        icon=ft.icons.PERSON,
                        icon_content=ft.Icon(ft.icons.PERSON, color="white"),
                        selected_icon_content=ft.Icon(ft.icons.PERSON, color="#2ECC71")
                        
                    )
                ],
                bgcolor='#2ECC71',
                indicator_color='#FFFFFF',
                scale=1.2,
                border=ft.border_radius.only(top_left=20, top_right=20)
            )
        else:
            page.navigation_bar = None
        page.update()

    def verificar_autenticacao():
        """Verifica dados da sessão diretamente do session_data"""
        user_id = page.session_data.get("user_id")
        user_type = page.session_data.get("user_type")
        return user_id, user_type

    async def rotas(e):
        page.controls.clear()
        appbar_profissional()
        navbar_profissional(False)

        try:
            rota = page.route

            if rota == '/logout':
                page.session_data.clear()
                page.controls.clear()
                await login(page)
                return

            if rota not in ["/login", "/registro", "/registro-profissional"]:
                user_id, user_type = verificar_autenticacao()
                if not user_id or not user_type:
                    page.go('/login')
                    return

            if rota == "/login":
                await login(page)
            elif rota == "/registro":
                await registro(page)
            elif rota == '/registro-profissional':
                await registro_profissional(page)
            elif rota == '/home-profissional':
                if user_type == "profissional":
                    await home_profissional(page)
                    navbar_profissional(True)
                else:
                    page.go('/login')
            elif rota == '/criar-profissional':
                if user_type == "profissional":
                    appbar_profissional("Criar Serviço", show_back=True)
                    navbar_profissional(True)
                    await criarServico(page)
                else:
                    page.go('/login')
            elif rota == '/servicos-solicitados':
                if user_type == "profissional":
                    appbar_profissional("Serviços Solicitados", show_back=True)
                    navbar_profissional(True)
                    await servicosSolicitados(page)
                else:
                    page.go('/login')
            elif rota == '/registros-servicos':
                if user_type == "profissional":
                   navbar_profissional(True)
                   appbar_profissional("Registro de Serviços", show_back=True)
                   await registrosServicos(page)
                else:
                    page.go('/login')
            elif rota == '/listar-servico':
                if user_type == "profissional":
                    appbar_profissional("Listar Serviço", show_back=True)
                    navbar_profissional(True)
                    await listarServico(page)
                else:
                    page.go('/login')
            elif rota == '/configuracao-profissional':
                if user_type == "profissional":
                    navbar_profissional(True)
                    appbar_profissional("Conta", show_back=True)
                    await configuracao(page)
                else:
                    page.go('/login')
            elif rota == '/home-usuario':
                if user_type == "usuario":
                    await home_usuario(page)
                    navbar_usuario(True)
                else:
                    page.go('/login')
            elif rota == '/configuracao-usuario':
                if user_type == "usuario":
                    await congfiguracao_usuario(page)
                    navbar_usuario(True)
                    appbar_usuario("Conta", show_back=True)
                else:
                    page.go('/login')
            elif rota == '/listar-eletricistas': 
                if user_type == "usuario":
                    navbar_usuario(True)
                    appbar_usuario("Eletricistas", show_back=True)
                    await listar_eletricistas(page)
                else:
                    page.go('/login')
            elif rota == '/listar-pintores': 
                if user_type == "usuario":
                    navbar_usuario(True)
                    appbar_usuario("Pintores", show_back=True)
                    await listar_pintores(page)
                else:
                    page.go('/login')
            elif rota == '/listar-jardineiros': 
                if user_type == "usuario":
                    navbar_usuario(True)
                    appbar_usuario("Jardineiros", show_back=True)
                    await listar_jardineiros(page)
                else:
                    page.go('/login')
            elif rota == '/contratar-servico': 
                if user_type == "usuario":
                    navbar_usuario(True)
                    appbar_usuario("Contrato", show_back=False)
                    await contratar(page)
                else:
                    page.go('/login')
            elif rota == '/pagamento-servico': 
                if user_type == "usuario":
                    navbar_usuario(True)
                    appbar_usuario("Pagamento", show_back=False)
                    await pagamentos(page)
                else:
                    page.go('/login')
            elif rota == '/conclusao-servico':
                if user_type == "usuario":
                    navbar_usuario(True)
                    appbar_usuario("Confirmar Serviço", show_back=True)
                    await conclusao_servico(page)
                else:
                    page.go('/login')
            elif rota == '/avaliar-servico':
                if user_type == "usuario":
                    navbar_usuario(True)
                    appbar_usuario("Avaliação", show_back=False)
                    await avaliar(page)
                else:
                    page.go('/login')

            page.update()

        except Exception as e:
            print(f"Erro ao processar rota: {e}")
            page.go('/login')

    page.on_route_change = rotas

    try:
        splash(page)
        page.update()
        await asyncio.sleep(2)

        page.controls.clear()
        apresentacao(page)
        page.update()
        await asyncio.sleep(3)

        page.controls.clear()
        await login(page)
        page.update()

    except Exception as e:
        print(f"Erro na inicialização: {e}")
        page.controls.clear()
        await login(page)
        page.update()

ft.app(
    target=main,
    assets_dir='assets',
    view=ft.AppView.FLET_APP
)