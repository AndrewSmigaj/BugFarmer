using UnityEngine;

namespace BugFarmer.Player
{
    /// <summary>
    /// Melee combat (sword/spear): sector query at swing start, optimistic hit-flash,
    /// server-validated damage via OpCode 88/89. Implemented with combat v1 (Phase 4.4);
    /// until then the router never routes here (this component is not attached).
    /// </summary>
    public class MeleeController : MonoBehaviour
    {
        /// <summary>Handle a routed left-click. Returns true if the swing was performed.</summary>
        public bool TryHandleClick()
        {
            return false; // combat v1 lands in Phase 4.4
        }
    }
}
