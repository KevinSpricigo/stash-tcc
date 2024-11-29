import flet as ft
from banco.conexao2 import supabase
from typing import List, Tuple, Any

async def obter_servicos_profissional(id_profissional: int) -> List[Tuple[Any, ...]]:
    try:
        resultado_profissional = supabase.table('profissionais')\
            .select('avatar_url')\
            .eq('id_profissional', id_profissional)\
            .execute()
            
        avatar_url = resultado_profissional.data[0].get('avatar_url') if resultado_profissional.data else None

        resultado_servicos = supabase.table('servicos')\
            .select('id_servico, nome, descricao, valor')\
            .eq('id_profissional', id_profissional)\
            .order('id_servico', desc=True)\
            .execute()

        servicos = []
        for servico in resultado_servicos.data:
            avaliacoes = supabase.table('avaliacoes')\
                .select('nota')\
                .eq('id_servico', servico['id_servico'])\
                .execute()
            
            total_avaliacoes = len(avaliacoes.data)
            media = sum(a['nota'] for a in avaliacoes.data) / total_avaliacoes if total_avaliacoes > 0 else 0
            
            servicos.append((
                servico['id_servico'],
                servico['nome'],
                servico['descricao'],
                servico['valor'],
                total_avaliacoes,
                media,
                avatar_url
            ))
            
        return servicos
    except Exception as e:
        print(f"Erro ao obter serviços: {e}")
        return []

async def excluir_servico_bd(id_servico: int) -> bool:
    try:
        pessoa_servicos = supabase.table('pessoa_servico')\
            .select('id_pessoa_servico')\
            .eq('id_servico', id_servico)\
            .execute()
        
        for ps in pessoa_servicos.data:
            supabase.table('pagamentos')\
                .delete()\
                .eq('id_pessoa_servico', ps['id_pessoa_servico'])\
                .execute()

        supabase.table('ordens')\
            .delete()\
            .eq('id_servico', id_servico)\
            .execute()

        supabase.table('pessoa_servico')\
            .delete()\
            .eq('id_servico', id_servico)\
            .execute()

        supabase.table('avaliacoes')\
            .delete()\
            .eq('id_servico', id_servico)\
            .execute()

        resultado = supabase.table('servicos')\
            .delete()\
            .eq('id_servico', id_servico)\
            .execute()

        return True
    except Exception as e:
        print(f"Erro ao excluir serviço: {e}")
        return False

async def listarServico(page: ft.Page):
    if not hasattr(page, 'session_data'):
        page.session_data = {}
        page.go('/login')
        return
    page.fonts = {
        'Poppins Medium': 'fonts/Poppins-Medium.ttf',
        'Poppins Regular': 'fonts/Poppins-Regular.ttf'
    }
    page.scroll = 'auto'
    page.title = 'STASH - Listar Serviço'

    id_profissional = page.session_data.get("user_id")
    if not id_profissional:
        page.go('/login')
        return
    servicos_bd = await obter_servicos_profissional(id_profissional)

    async def criar_item_servico(servico):
        id_servico, nome, descricao, valor, total_avaliacoes, media, avatar_url = servico

        async def excluir_servico(e):
            if await excluir_servico_bd(id_servico):
                snack = ft.SnackBar(content=ft.Text("Serviço excluído com sucesso!"))
                page.overlay.append(snack)
                snack.open = True
                page.controls.clear()
                
                servicos_atualizados = await obter_servicos_profissional(id_profissional)
                servicos_widgets = [await criar_item_servico(s) for s in servicos_atualizados]
                
                if not servicos_widgets:
                    page.add(
                        ft.Container(
                            content=ft.Text("Nenhum serviço cadastrado", size=16, color='black'),
                            alignment=ft.alignment.center,
                            margin=ft.margin.only(top=50)
                        )
                    )
                else:
                    page.add(ft.Column(controls=servicos_widgets, scroll=ft.ScrollMode.AUTO))
                
                page.update()
            else:
                snack = ft.SnackBar(content=ft.Text("Erro ao excluir serviço"))
                page.overlay.append(snack)
                snack.open = True
                page.update()

        return ft.Container(
            content=ft.Row(
                controls=[
                    ft.Container(
                        ft.CircleAvatar(
                            foreground_image_url=avatar_url if avatar_url else None,
                            content=ft.Icon(ft.icons.PERSON) if not avatar_url else None,
                            radius=35
                        ),
                        padding=ft.padding.only(top=-100, left=10, right=10, bottom=0)
                    ),
                    ft.Column([
                        ft.Row(
                            [
                                ft.Container(
                                    content=ft.Text(
                                        value=nome,
                                        size=16,
                                        color='black',
                                        font_family='Poppins Medium'
                                    ),
                                    expand=True
                                ),
                                ft.Container(
                                    content=ft.Text(
                                        value=f'R${valor:.2f}',
                                        color='black',
                                        size=16,
                                        font_family='Poppins Regular'
                                    ),
                                    alignment=ft.alignment.center_right
                                )
                            ],
                            width=250
                        ),
                        ft.Row(
                            [
                                ft.Icon(ft.icons.STAR, size=20, color='black'),
                                ft.Text(
                                    value=f'{media:.1f}',
                                    color='black',
                                    size=14,
                                    font_family='Poppins Regular'
                                ),
                                ft.Text(
                                    value=f'({total_avaliacoes} avaliações)',
                                    color='black',
                                    font_family='Poppins Regular',
                                    size=10
                                ),
                                ft.Container(width=50, height=0),
                                ft.IconButton(
                                    icon=ft.icons.CLOSE,
                                    icon_color='red',
                                    icon_size=16,
                                    tooltip='Apagar serviço',
                                    on_click=excluir_servico
                                )
                            ],
                            spacing=5
                        ),
                        ft.Row(),
                        ft.Row(
                            [
                                ft.TextField(
                                    multiline=True,
                                    min_lines=3,
                                    max_lines=3,
                                    width=225,
                                    hint_text='Descrição',
                                    read_only=True,
                                    color='black',
                                    text_size=12,
                                    value=descricao
                                )
                            ],
                            alignment=ft.MainAxisAlignment.START
                        )
                    ]),
                ],
            ),
            padding=ft.padding.only(bottom=20)
        )

    servicos_widgets = [await criar_item_servico(servico) for servico in servicos_bd]

    if not servicos_widgets:
        page.add(
            ft.Container(
                content=ft.Text(
                    "Nenhum serviço cadastrado",
                    size=16,
                    color='black'
                ),
                alignment=ft.alignment.center,
                margin=ft.margin.only(top=50)
            )
        )
    else:
        page.add(ft.Column(controls=servicos_widgets, scroll=ft.ScrollMode.AUTO))