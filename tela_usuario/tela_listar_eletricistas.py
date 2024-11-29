import flet as ft
from banco.conexao2 import supabase

async def listar_eletricistas(page: ft.Page):
    if not hasattr(page, 'session_data'):
        page.session_data = {}
        page.go('/login')
        return

    page.bgcolor = '#FFFFFF'
    page.scroll = ft.ScrollMode.AUTO
    
    grid = ft.Container(
        content=ft.Column(
            controls=[],
            scroll=ft.ScrollMode.AUTO,
            spacing=10,
        ),
        alignment=ft.alignment.top_center,
        padding=ft.padding.only(left=10, right=10, top=10)
    )

    def contratar(e, servico_id):
        page.session_data["servico_selecionado"] = servico_id
        page.go('/contratar-servico')

    try:
        profissionais = supabase.table('profissionais')\
            .select('id_profissional, nome, sobrenome, status, avatar_url')\
            .eq('profissao', 'Eletricista')\
            .eq('status', 'Disponível')\
            .execute()

        if not profissionais.data:
            grid.content.controls.append(
                ft.Container(
                    content=ft.Text(
                        "Nenhum eletricista disponível no momento.",
                        size=16,
                        color='black',
                        text_align=ft.TextAlign.CENTER
                    ),
                    margin=ft.margin.only(top=50),
                    alignment=ft.alignment.center
                )
            )
        else:
            for profissional in profissionais.data:
                servicos = supabase.table('servicos')\
                    .select('id_servico, nome, descricao, valor')\
                    .eq('id_profissional', profissional['id_profissional'])\
                    .execute()

                if servicos.data:
                    for servico in servicos.data:
                        avaliacoes = supabase.table('avaliacoes')\
                            .select('nota')\
                            .eq('id_servico', servico['id_servico'])\
                            .execute()
                        
                        total_avaliacoes = len(avaliacoes.data)
                        media_avaliacoes = sum(a['nota'] for a in avaliacoes.data) / total_avaliacoes if total_avaliacoes > 0 else 0

                        card = ft.Container(
                            content=ft.Row(
                                controls=[
                                    ft.Container(
                                        ft.CircleAvatar(
                                            foreground_image_url=profissional.get('avatar_url') if profissional.get('avatar_url') else None,
                                            content=ft.Icon(ft.icons.PERSON) if not profissional.get('avatar_url') else None,
                                            radius=35
                                        ),
                                        padding=ft.padding.only(top=-100, left=10, right=10, bottom=0)
                                    ),
                                    ft.Column([
                                        ft.Row(
                                            [
                                                ft.Container(
                                                    content=ft.Text(
                                                        value=f"{profissional['nome']} {profissional['sobrenome']}",
                                                        size=16,
                                                        font_family='Poppins Medium',
                                                        color='black'
                                                    ),
                                                    expand=True
                                                ),
                                                ft.Container(
                                                    content=ft.Text(
                                                        value=f"R$ {servico['valor']:.2f}",
                                                        size=16,
                                                        font_family='Poppins Regular',
                                                        color='black'
                                                    ),
                                                    alignment=ft.alignment.center_right
                                                )
                                            ],
                                            width=200
                                        ),
                                        ft.Row(
                                            [
                                                ft.Icon(ft.icons.STAR, size=20, color='black'),
                                                ft.Text(
                                                    value=f'{media_avaliacoes:.1f}',
                                                    size=14,
                                                    font_family='Poppins Regular',
                                                    color='black'
                                                ),
                                                ft.Text(
                                                    value=f'({total_avaliacoes} avaliações)',
                                                    font_family='Poppins Regular',
                                                    size=10,
                                                    color='black'
                                                ),
                                                ft.Container(width=50, height=0),
                                                ft.IconButton(
                                                    icon=ft.icons.CHECK,
                                                    icon_color='green',
                                                    icon_size=16,
                                                    tooltip='Contratar serviço',
                                                    on_click=lambda e, s=servico['id_servico']: contratar(e, s)
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
                                                    text_size=12,
                                                    color='black',
                                                    value=servico['descricao'] or "Sem descrição disponível"
                                                )
                                            ],
                                            alignment=ft.MainAxisAlignment.START
                                        )
                                    ]),
                                ],
                            ),
                            padding=ft.padding.only(left=0,right=0,top=10,bottom=10),
                            margin=ft.margin.only(bottom=10, left=0, right=10),
                            border=ft.border.all(1, ft.colors.GREY_300),
                            border_radius=10
                        )
                        grid.content.controls.append(card)

    except Exception as e:
        print(f"Erro ao listar eletricistas: {e}")
        grid.content.controls.append(
            ft.Container(
                content=ft.Text(
                    f"Erro ao carregar eletricistas: {str(e)}",
                    color="red",
                    size=16,
                    text_align=ft.TextAlign.CENTER
                ),
                margin=ft.margin.only(top=50),
                alignment=ft.alignment.center
            )
        )

    page.add(grid)