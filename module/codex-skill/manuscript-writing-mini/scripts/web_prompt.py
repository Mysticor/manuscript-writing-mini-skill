"""Generate an on-demand web writing prompt from maintained rules (not a tool installer)."""
import argparse, hashlib
from pathlib import Path

SOURCES = ('SKILL.md', 'references/workflow.md', 'references/writing-safety.md',
           'references/targeted-source-verification.md', 'references/citation-planning.md',
           'references/readiness-gates.md')

def render(root):
    sources = [(name, root/name) for name in SOURCES]
    sources.append(('workflow-contract/portable-work.md', root.parents[2]/'workflow-contract/portable-work.md'))
    parts = ['# 写作mini：网页协作入口（自动生成）\n\n'
             '这是当前写作批次的指令，不是完整软件安装或全部绘图资源。先让用户提供当前项目工作包、真实证据和本轮范围；'
             '已有信息直接使用。以下规则适用于文本写作和接续；涉及绘图、脚本校验或正式交接时必须读取原Skill相应资源，'
             '缺失则列待补或回交本地，不能自行补造工具、事实、Gate或验收结果。\n\n'
             '保持原阶段停顿和用户确认。无本地浏览器不执行机构登录；无文件工具不声称生成ZIP。'
             '运行环境以当前实际能力为准。\n\n'
             '来源文件及SHA256如下；修改源规则后重新生成，不手工维护此派生文本。\n']
    loaded = [(name, p.read_text()) for name,p in sources]  # fail before output if incomplete
    for name,text in loaded:
        parts.append(f'- {name}: {hashlib.sha256(text.encode()).hexdigest()}\n')
    for name,text in loaded:
        parts.append(f'\n\n---\n## 来源：{name}\n\n{text}')
    return ''.join(parts)

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out',required=True)
    args=parser.parse_args()
    text=render(Path(__file__).resolve().parents[1])
    with Path(args.out).open('x', encoding='utf-8') as f: f.write(text)
if __name__=='__main__': main()
