// Darkness overlay for the underground lighting system (URP-native).
// Multiply blend: the framebuffer (the already-lit scene) is multiplied by this sprite's texture.
//   result = src.rgb * dst.rgb   (Blend DstColor Zero)
// A BLACK texel -> that pixel goes black; a WHITE texel -> unchanged. So a per-cell darkness map
// (1 = lit, 0 = dark) darkens roofed/buried cells while leaving the lit surface untouched — even at
// noon, because it multiplies the FINAL lit color rather than adding into the 2D light accumulation.
// Runs on a SpriteRenderer sorted above all world content, below the ScreenSpaceOverlay UI.
Shader "BugFarmer/DarknessMultiply"
{
    Properties
    {
        [PerRendererData] _MainTex ("Darkness", 2D) = "white" {}
    }
    SubShader
    {
        Tags
        {
            "RenderPipeline"="UniversalPipeline"
            "Queue"="Transparent"
            "RenderType"="Transparent"
            "IgnoreProjector"="True"
            "PreviewType"="Plane"
            "CanUseSpriteAtlas"="True"
        }
        Cull Off
        Lighting Off
        ZWrite Off
        Blend DstColor Zero   // multiply the framebuffer by frag.rgb

        Pass
        {
            HLSLPROGRAM
            #pragma vertex vert
            #pragma fragment frag
            #include "Packages/com.unity.render-pipelines.universal/ShaderLibrary/Core.hlsl"

            struct Attributes
            {
                float3 positionOS : POSITION;
                float2 uv         : TEXCOORD0;
            };

            struct Varyings
            {
                float4 positionHCS : SV_POSITION;
                float2 uv          : TEXCOORD0;
            };

            TEXTURE2D(_MainTex);
            SAMPLER(sampler_MainTex);

            Varyings vert(Attributes IN)
            {
                Varyings OUT;
                OUT.positionHCS = TransformObjectToHClip(IN.positionOS);
                OUT.uv = IN.uv;
                return OUT;
            }

            half4 frag(Varyings IN) : SV_Target
            {
                half4 d = SAMPLE_TEXTURE2D(_MainTex, sampler_MainTex, IN.uv);
                // Under Blend DstColor Zero only .rgb matters; alpha is ignored by the blend.
                return half4(d.rgb, 1.0);
            }
            ENDHLSL
        }
    }
    Fallback Off
}
