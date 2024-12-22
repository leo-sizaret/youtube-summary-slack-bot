prompts = [
    """
    Write an insightful summary of this video that helps viewers understand the deeper implications of the discussion. 
    Explain the reasoning behind key arguments and how different ideas connect. 
    Write as if explaining to a curious person who wants to understand not just what was said, but why it matters. 
    Use the timestamps provided to reference when key points are discussed.

    Format your response like this:

    *TLDR*
    Explain the big picture context of this discussion and the 1-2 key takeaways.

    Separate this section with the next with "----------------"

    *Key arguments* (MM:SS)
    For each major point, include its timestamp and explain:
    - The core argument being made, explained in detail. IMPORTANT: be longer rather than shorter. More information is better.
    - The reasoning and evidence behind it
    - Why this matters and its broader implications

    Each major point should be bolded using * and sub-points should have - bullets
    The casing should be sentence case, like this: "*Major point*"

    *Implications for StarkWare*
    Analyze any implications for StarkWare based on the discussion. Consider:
    - Impact on L2 scaling solutions
    - Relevance to StarkWare's technology and value proposition
    - Potential strategic considerations

    Be intelligent about the implciations. If there are no clear implications, simply state "No direct implications for StarkWare from this discussion."

    Keep the language conversational but substantive. Help readers understand both what the speakers think AND why they think it.

    Be clear.

    Don't be afraid to be controversial. Substance is the most important.

    Here is an example of how to phrase and format the output:

    Don't add anything before the TLDR, like declaring that you are providing a summary or such introductory things. Only write from the TLDR onwards.

    '''
    *TLDR:* This conversation explores how meme coins, AI, and Trump's potential presidency intersect with deeper trends in crypto markets, revealing tensions between technical utility and community/cultural value in determining crypto asset prices.

    ----------------

    *Trump's Impact Goes Beyond Politics* (timestamp in MM:SS format)
    - The speakers argue that Trump's monetary policy would likely benefit crypto, but not for the obvious regulatory reasons. 
    - Their key insight is that Trump's aggressive money printing stance would fundamentally weaken the dollar, pushing investors toward "hard" assets. 
    - More importantly, they suggest this could redefine what makes a cryptocurrency valuable - it's not about technology or regulation, but about being an alternative to traditional currency.

    *Meme Coins Reveal a Deeper Truth* (timestamp in MM:SS format)
    - Rather than dismissing meme coins as jokes, the speakers see them as proving something profound about crypto markets: that community belief and engagement create more sustainable value than technical features. 
    - They point to how meme coins, despite their simplicity, often maintain value better than technically sophisticated projects. 
    - This challenges the industry's focus on technological complexity.

    *Ethereum's Identity Crisis* (timestamp in MM:SS format)
    - The debate about Ethereum's future isn't just about technology - it's about the fundamental nature of value in crypto. 
    - Hayes sees ETH as primarily a commodity (like digital oil) because its value comes from its usefulness in computing. 
    - However, Mirad argues this view might limit ETH's potential, suggesting that without monetary premium (people viewing it as a form of money), ETH might not sustain high valuations. This reflects a larger debate about whether utility or monetary properties drive long-term crypto value.

    *AI's Disruptive Potential* (timestamp in MM:SS format)
    - The speakers reveal an unexpected insight about AI in crypto: as AI makes technical development easier, the value of complex technical solutions might actually decrease. 
    - They suggest this could shift value toward community and brand-driven projects, as technical barriers become less relevant. 
    - This challenges the common assumption that technical sophistication equals value in crypto.

    *Implications for StarkWare*
    ...
    '''
    """
]