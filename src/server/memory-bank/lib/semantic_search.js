import { pipeline } from '@xenova/transformers';

let embedder = null;

// Initialize the embedding model (lazy loading)
async function getEmbedder() {
    if (!embedder) {
        embedder = await pipeline('feature-extraction', 'Xenova/all-MiniLM-L6-v2');
    }
    return embedder;
}

// Calculate cosine similarity between two vectors
function cosineSimilarity(vecA, vecB) {
    const dotProduct = vecA.reduce((sum, a, i) => sum + a * vecB[i], 0);
    const magnitudeA = Math.sqrt(vecA.reduce((sum, a) => sum + a * a, 0));
    const magnitudeB = Math.sqrt(vecB.reduce((sum, b) => sum + b * b, 0));
    return dotProduct / (magnitudeA * magnitudeB);
}

// Encode text to vector
export async function encodeText(text) {
    try {
        const model = await getEmbedder();
        const output = await model(text, { pooling: 'mean', normalize: true });
        return Array.from(output.data);
    } catch (error) {
        console.error('Error encoding text:', error);
        return null;
    }
}

// Find the most similar long-term memories to a query
export async function findSimilarMemories(queryText, longTermMemories, topK = 3) {
    if (!queryText || !longTermMemories || longTermMemories.length === 0) {
        return [];
    }

    try {
        // Encode the query
        const queryVector = await encodeText(queryText);
        if (!queryVector) {
            return [];
        }

        // Calculate similarities
        const similarities = [];
        for (const memory of longTermMemories) {
            if (memory.embedding) {
                const similarity = cosineSimilarity(queryVector, memory.embedding);
                similarities.push({
                    memory: memory,
                    similarity: similarity
                });
            }
        }

        // Sort by similarity and return top K
        similarities.sort((a, b) => b.similarity - a.similarity);
        return similarities.slice(0, topK).map(item => ({
            content: item.memory.content,
            timestamp: item.memory.timestamp,
            similarity: item.similarity
        }));

    } catch (error) {
        console.error('Error finding similar memories:', error);
        return [];
    }
} 