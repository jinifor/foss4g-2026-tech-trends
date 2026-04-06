import { useMemo, useState } from "react";

import type { ClusterGroup, NetworkLink, NetworkNode } from "@/types/dashboard";

type PositionedNode = NetworkNode & { x: number; y: number; color: string };
type HoverState =
  | { type: "node"; id: string }
  | { type: "link"; key: string; source: string; target: string }
  | null;

export function KeywordNetwork({
  nodes,
  links,
  clusters,
}: {
  nodes: NetworkNode[];
  links: NetworkLink[];
  clusters: ClusterGroup[];
}) {
  const [hoveredItem, setHoveredItem] = useState<HoverState>(null);
  const { positionedNodes, filteredLinks, clusterLabels } = useMemo(() => {
    const filteredNodes = nodes.slice(0, 24);
    const nodesByCluster = new Map<string, NetworkNode[]>();
    filteredNodes.forEach((node) => {
      const bucket = nodesByCluster.get(node.cluster) ?? [];
      bucket.push(node);
      nodesByCluster.set(node.cluster, bucket);
    });

    const orderedClusters = clusters.filter((cluster) => nodesByCluster.has(cluster.id));
    const totalWidth = 1280;
    const gap = orderedClusters.length > 1 ? (totalWidth - 240) / (orderedClusters.length - 1) : 0;
    const positionedNodes: PositionedNode[] = [];

    orderedClusters.forEach((cluster, clusterIndex) => {
      const bucket = (nodesByCluster.get(cluster.id) ?? []).sort((a, b) => b.count - a.count);
      const x = 120 + clusterIndex * gap;
      const verticalGap = bucket.length > 1 ? 540 / (bucket.length - 1) : 0;
      bucket.forEach((node, nodeIndex) => {
        positionedNodes.push({
          ...node,
          x,
          y: 110 + nodeIndex * verticalGap,
          color: cluster.color,
        });
      });
    });

    const nodeLookup = new Map(positionedNodes.map((node) => [node.id, node]));
    const filteredLinks = links
      .filter((link) => nodeLookup.has(link.source) && nodeLookup.has(link.target))
      .sort((a, b) => b.count - a.count)
      .slice(0, 58);

    return {
      positionedNodes,
      filteredLinks,
      clusterLabels: orderedClusters,
    };
  }, [clusters, links, nodes]);

  const nodeLookup = useMemo(() => new Map(positionedNodes.map((node) => [node.id, node])), [positionedNodes]);
  const { activeNodeIds, activeLinkKeys, activeClusterIds } = useMemo(() => {
    if (!hoveredItem) {
      return {
        activeNodeIds: null,
        activeLinkKeys: null,
        activeClusterIds: null,
      };
    }

    const nextActiveNodeIds = new Set<string>();
    const nextActiveLinkKeys = new Set<string>();

    if (hoveredItem.type === "node") {
      nextActiveNodeIds.add(hoveredItem.id);
      filteredLinks.forEach((link) => {
        if (link.source === hoveredItem.id || link.target === hoveredItem.id) {
          nextActiveLinkKeys.add(`${link.source}-${link.target}`);
          nextActiveNodeIds.add(link.source);
          nextActiveNodeIds.add(link.target);
        }
      });
    } else {
      nextActiveLinkKeys.add(hoveredItem.key);
      nextActiveNodeIds.add(hoveredItem.source);
      nextActiveNodeIds.add(hoveredItem.target);
    }

    const nextActiveClusterIds = new Set<string>();
    nextActiveNodeIds.forEach((nodeId) => {
      const node = nodeLookup.get(nodeId);
      if (node) {
        nextActiveClusterIds.add(node.cluster);
      }
    });

    return {
      activeNodeIds: nextActiveNodeIds,
      activeLinkKeys: nextActiveLinkKeys,
      activeClusterIds: nextActiveClusterIds,
    };
  }, [filteredLinks, hoveredItem, nodeLookup]);
  const maxCount = Math.max(...positionedNodes.map((node) => node.count), 1);
  const maxLink = Math.max(...filteredLinks.map((link) => link.count), 1);

  return (
    <div
      className="overflow-auto rounded-[1.75rem] border border-border/60 bg-white/70"
      onMouseLeave={() => setHoveredItem(null)}
    >
      <svg viewBox="0 0 1280 700" className="min-h-[700px] w-full min-w-[980px]">
        {clusterLabels.map((cluster) => {
          const clusterNodes = positionedNodes.filter((node) => node.cluster === cluster.id);
          if (!clusterNodes.length) return null;
          const x = clusterNodes[0].x;
          const isActiveCluster = !activeClusterIds || activeClusterIds.has(cluster.id);
          return (
            <g key={cluster.id} opacity={isActiveCluster ? 1 : 0.3}>
              <rect
                x={x - 92}
                y={34}
                width={184}
                height={44}
                rx={22}
                fill={cluster.color}
                fillOpacity={isActiveCluster ? 0.18 : 0.08}
                style={{ transition: "opacity 160ms ease, fill-opacity 160ms ease" }}
              />
              <text
                x={x}
                y={62}
                textAnchor="middle"
                fontSize="15"
                fontWeight="700"
                fill="#173640"
                style={{ transition: "opacity 160ms ease" }}
              >
                {cluster.name}
              </text>
            </g>
          );
        })}

        {filteredLinks.map((link, index) => {
          const source = nodeLookup.get(link.source);
          const target = nodeLookup.get(link.target);
          if (!source || !target) return null;
          const key = `${link.source}-${link.target}`;
          const midX = (source.x + target.x) / 2;
          const lift = 42 + (index % 6) * 12;
          const path = `M ${source.x} ${source.y} C ${midX} ${source.y - lift}, ${midX} ${target.y + lift}, ${target.x} ${target.y}`;
          const baseStrokeWidth = 1.5 + (link.count / maxLink) * 4;
          const isActiveLink = !activeLinkKeys || activeLinkKeys.has(key);
          const isHoveredLink = hoveredItem?.type === "link" && hoveredItem.key === key;
          return (
            <g
              key={key}
              onMouseEnter={() => setHoveredItem({ type: "link", key, source: link.source, target: link.target })}
              onMouseLeave={() => setHoveredItem(null)}
              style={{ cursor: "pointer" }}
            >
              <path d={path} fill="none" stroke="transparent" strokeWidth={Math.max(baseStrokeWidth + 14, 16)} strokeLinecap="round" />
              <path
                d={path}
                fill="none"
                stroke={isHoveredLink ? "rgba(23,126,137,0.92)" : isActiveLink ? "rgba(23,126,137,0.62)" : "rgba(23,126,137,0.08)"}
                strokeWidth={isHoveredLink ? baseStrokeWidth + 2.5 : isActiveLink ? baseStrokeWidth + 0.8 : Math.max(baseStrokeWidth - 0.5, 1)}
                strokeLinecap="round"
                style={{ transition: "stroke 160ms ease, stroke-width 160ms ease, opacity 160ms ease" }}
              >
                <title>{`${link.source} ↔ ${link.target}: ${link.count} talks`}</title>
              </path>
            </g>
          );
        })}

        {positionedNodes.map((node) => {
          const baseRadius = 10 + (node.count / maxCount) * 18;
          const isActiveNode = !activeNodeIds || activeNodeIds.has(node.id);
          const isHoveredNode = hoveredItem?.type === "node" && hoveredItem.id === node.id;
          const radius = isHoveredNode ? baseRadius + 3 : isActiveNode && hoveredItem ? baseRadius + 1.5 : baseRadius;
          return (
            <g
              key={node.id}
              onMouseEnter={() => setHoveredItem({ type: "node", id: node.id })}
              onMouseLeave={() => setHoveredItem(null)}
              style={{ cursor: "pointer" }}
            >
              <circle
                cx={node.x}
                cy={node.y}
                r={radius + (isHoveredNode ? 11 : 8)}
                fill={node.color}
                fillOpacity={isHoveredNode ? 0.26 : isActiveNode ? 0.16 : 0.05}
                style={{ transition: "r 160ms ease, fill-opacity 160ms ease" }}
              />
              <circle
                cx={node.x}
                cy={node.y}
                r={radius}
                fill={node.color}
                fillOpacity={isActiveNode ? 0.92 : 0.24}
                stroke="rgba(255,255,255,0.92)"
                strokeWidth={isHoveredNode ? 3 : isActiveNode ? 2 : 1}
                style={{ transition: "r 160ms ease, fill-opacity 160ms ease, stroke-width 160ms ease" }}
              >
                <title>{`${node.keyword}: ${node.count} talks · ${node.degree} links`}</title>
              </circle>
              <text
                x={node.x}
                y={node.y + radius + 18}
                textAnchor="middle"
                fontSize="13"
                fontWeight={isHoveredNode ? "800" : "700"}
                fill={isActiveNode ? "#173640" : "rgba(23,54,64,0.34)"}
                style={{ transition: "fill 160ms ease, opacity 160ms ease" }}
              >
                {node.keyword}
              </text>
            </g>
          );
        })}
      </svg>
    </div>
  );
}
