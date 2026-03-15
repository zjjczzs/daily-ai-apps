#!/usr/bin/env python3
"""
AutoResearch Assistant - 自主研究助手
基于当前最热门的AI趋势：Autonomous Research/Autoresearch

功能：自动搜索、分析、总结任何主题，并生成研究报告
"""

import os
import sys
import json
import asyncio
import argparse
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path

from dotenv import load_dotenv
from pydantic import BaseModel, Field
from openai import AsyncOpenAI
from duckduckgo_search import DDGS

# 加载环境变量
load_dotenv()


class SearchResult(BaseModel):
    """搜索结果模型"""
    title: str
    url: str
    snippet: str
    source: str = "duckduckgo"


class ResearchFinding(BaseModel):
    """研究发现模型"""
    insight: str
    evidence: List[str]
    confidence: str = Field(default="medium", pattern="^(high|medium|low)$")


class ResearchReport(BaseModel):
    """研究报告模型"""
    topic: str
    summary: str
    key_findings: List[ResearchFinding]
    detailed_analysis: str
    sources: List[Dict[str, str]]
    research_rounds: int
    generated_at: str
    
    def to_markdown(self) -> str:
        """转换为Markdown格式"""
        md = f"""# 研究报告: {self.topic}

> 生成时间: {self.generated_at}
> 研究轮次: {self.research_rounds}

## 执行摘要

{self.summary}

## 关键发现

"""
        for i, finding in enumerate(self.key_findings, 1):
            md += f"""### {i}. {finding.insight[:50]}...

- **可信度**: {finding.confidence}
- **证据**:
"""
            for ev in finding.evidence[:3]:
                md += f"  - {ev[:100]}...\n"
            md += "\n"
        
        md += f"""## 详细分析

{self.detailed_analysis}

## 信息来源

"""
        for i, source in enumerate(self.sources, 1):
            md += f"{i}. [{source.get('title', 'Unknown')}]({source.get('url', '#')})\n"
        
        return md


@dataclass
class ResearchConfig:
    """研究配置"""
    depth: str = "medium"  # shallow, medium, deep
    max_rounds: int = 5
    max_results_per_query: int = 10
    
    @property
    def target_rounds(self) -> int:
        rounds_map = {"shallow": 2, "medium": 4, "deep": 6}
        return rounds_map.get(self.depth, 4)


class AutoResearcher:
    """自主研究助手"""
    
    def __init__(self, config: Optional[ResearchConfig] = None):
        self.config = config or ResearchConfig()
        self.client = AsyncOpenAI(
            api_key=os.getenv("OPENAI_API_KEY"),
            base_url=os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
        )
        self.model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
        self.all_results: List[SearchResult] = []
        self.all_insights: List[str] = []
        
    async def search(self, query: str, max_results: int = 10) -> List[SearchResult]:
        """执行搜索"""
        results = []
        try:
            with DDGS() as ddgs:
                for r in ddgs.text(query, max_results=max_results):
                    result = SearchResult(
                        title=r.get("title", ""),
                        url=r.get("href", ""),
                        snippet=r.get("body", "")
                    )
                    results.append(result)
                    self.all_results.append(result)
        except Exception as e:
            print(f"搜索出错: {e}")
        return results
    
    async def analyze_results(self, query: str, results: List[SearchResult]) -> Dict[str, Any]:
        """使用LLM分析搜索结果"""
        if not results:
            return {"insights": [], "follow_up_queries": []}
        
        content = "\n\n".join([
            f"标题: {r.title}\n摘要: {r.snippet}\n链接: {r.url}"
            for r in results[:5]
        ])
        
        prompt = f"""你是一位专业的研究分析师。基于以下搜索结果，分析关于"{query}"的信息。

搜索结果:
{content}

请提供以下JSON格式的分析（只返回JSON，不要其他文字）:
{{
    "insights": [
        "关键发现1",
        "关键发现2"
    ],
    "follow_up_queries": [
        "需要深入搜索的后续问题1",
        "需要深入搜索的后续问题2"
    ],
    "confidence": "high|medium|low"
}}
"""
        
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "你是一个专业的研究分析师，擅长从搜索结果中提取关键信息。"},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3
            )
            
            content = response.choices[0].message.content
            # 提取JSON部分
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0]
            elif "```" in content:
                content = content.split("```")[1].split("```")[0]
            
            analysis = json.loads(content.strip())
            
            # 保存insights
            for insight in analysis.get("insights", []):
                self.all_insights.append(insight)
            
            return analysis
        except Exception as e:
            print(f"分析出错: {e}")
            return {"insights": [], "follow_up_queries": [], "confidence": "low"}
    
    async def generate_queries(self, topic: str) -> List[str]:
        """生成初始搜索查询"""
        prompt = f"""为研究主题"{topic}"生成3-5个不同的搜索查询角度。

请返回JSON格式（只返回JSON）:
{{
    "queries": [
        "查询1",
        "查询2",
        "查询3"
    ]
}}
"""
        
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "你是一个研究专家，擅长从不同角度思考研究主题。"},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.5
            )
            
            content = response.choices[0].message.content
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0]
            elif "```" in content:
                content = content.split("```")[1].split("```")[0]
            
            data = json.loads(content.strip())
            return data.get("queries", [topic])
        except Exception as e:
            print(f"生成查询出错: {e}")
            return [topic, f"{topic} 最新进展", f"{topic} 教程"]
    
    async def research(self, topic: str) -> ResearchReport:
        """执行自主研究"""
        print(f"🔍 开始研究: {topic}")
        print(f"📊 研究深度: {self.config.depth} (目标轮次: {self.config.target_rounds})")
        
        # 生成初始查询
        queries = await self.generate_queries(topic)
        print(f"📝 生成 {len(queries)} 个初始查询")
        
        # 执行研究循环
        round_num = 0
        pending_queries = queries[:]
        
        while round_num < self.config.target_rounds and pending_queries:
            round_num += 1
            print(f"\n🔄 研究轮次 {round_num}/{self.config.target_rounds}")
            
            # 取当前轮次的查询
            current_queries = pending_queries[:2]  # 每轮最多2个查询
            pending_queries = pending_queries[2:]
            
            # 执行搜索和分析
            for query in current_queries:
                print(f"  搜索: {query[:50]}...")
                results = await self.search(query, self.config.max_results_per_query)
                print(f"    找到 {len(results)} 条结果")
                
                if results:
                    analysis = await self.analyze_results(query, results)
                    
                    # 添加后续查询
                    follow_ups = analysis.get("follow_up_queries", [])
                    for fu in follow_ups[:2]:  # 每轮最多添加2个后续查询
                        if fu not in pending_queries and len(pending_queries) < 6:
                            pending_queries.append(fu)
        
        print(f"\n✅ 研究完成，共 {round_num} 轮，收集 {len(self.all_results)} 条结果")
        
        # 生成最终报告
        return await self._generate_report(topic, round_num)
    
    async def _generate_report(self, topic: str, rounds: int) -> ResearchReport:
        """生成最终研究报告"""
        print("📝 生成研究报告...")
        
        # 准备分析材料
        insights_text = "\n".join([f"- {i}" for i in self.all_insights[:15]])
        sources_text = "\n".join([
            f"标题: {r.title}\n摘要: {r.snippet[:200]}"
            for r in self.all_results[:10]
        ])
        
        prompt = f"""基于以下研究发现，生成一份完整的研究报告。

研究主题: {topic}

关键发现:
{insights_text}

来源摘要:
{sources_text}

请提供以下JSON格式的报告（只返回JSON）:
{{
    "summary": "执行摘要（200字左右）",
    "key_findings": [
        {{
            "insight": "发现1的详细描述",
            "evidence": ["证据1", "证据2"],
            "confidence": "high"
        }}
    ],
    "detailed_analysis": "详细分析（500字左右）"
}}
"""
        
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "你是一个专业的研究报告撰写专家。"},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.4
            )
            
            content = response.choices[0].message.content
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0]
            elif "```" in content:
                content = content.split("```")[1].split("```")[0]
            
            report_data = json.loads(content.strip())
            
            # 构建来源列表
            sources = [
                {"title": r.title, "url": r.url}
                for r in self.all_results[:20]
            ]
            
            # 构建关键发现
            key_findings = []
            for kf in report_data.get("key_findings", []):
                key_findings.append(ResearchFinding(
                    insight=kf.get("insight", ""),
                    evidence=kf.get("evidence", []),
                    confidence=kf.get("confidence", "medium")
                ))
            
            return ResearchReport(
                topic=topic,
                summary=report_data.get("summary", ""),
                key_findings=key_findings,
                detailed_analysis=report_data.get("detailed_analysis", ""),
                sources=sources,
                research_rounds=rounds,
                generated_at=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            )
            
        except Exception as e:
            print(f"生成报告出错: {e}")
            # 返回基本报告
            return ResearchReport(
                topic=topic,
                summary=f"关于{topic}的研究",
                key_findings=[],
                detailed_analysis="",
                sources=[{"title": r.title, "url": r.url} for r in self.all_results[:10]],
                research_rounds=rounds,
                generated_at=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            )


async def main():
    parser = argparse.ArgumentParser(description="AutoResearch Assistant - 自主研究助手")
    parser.add_argument("topic", help="研究主题")
    parser.add_argument("--depth", choices=["shallow", "medium", "deep"], 
                       default=os.getenv("DEFAULT_RESEARCH_DEPTH", "medium"),
                       help="研究深度")
    parser.add_argument("--output", "-o", help="输出文件路径")
    parser.add_argument("--model", default=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
                       help="使用的模型")
    
    args = parser.parse_args()
    
    # 检查API Key
    if not os.getenv("OPENAI_API_KEY"):
        print("❌ 错误: 请设置 OPENAI_API_KEY 环境变量")
        print("   可以复制 .env.example 为 .env 并填写配置")
        sys.exit(1)
    
    # 创建配置
    config = ResearchConfig(
        depth=args.depth,
        max_rounds=int(os.getenv("MAX_SEARCH_ROUNDS", 5)),
        max_results_per_query=int(os.getenv("MAX_RESULTS_PER_QUERY", 10))
    )
    
    # 执行研究
    researcher = AutoResearcher(config)
    report = await researcher.research(args.topic)
    
    # 输出报告
    markdown = report.to_markdown()
    
    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(markdown)
        print(f"\n✅ 报告已保存到: {args.output}")
    else:
        print("\n" + "="*60)
        print(markdown)
        print("="*60)


if __name__ == "__main__":
    asyncio.run(main())
